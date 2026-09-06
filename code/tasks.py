import cv2
import numpy as np
import rasterio
from pathlib import Path
from PIL import Image

def load_image(path):
    if path.lower().endswith((".tif", ".tiff")):
        with rasterio.open(path) as src:
            arr = src.read()
            arr = np.transpose(arr, (1, 2, 0))
            arr = arr[:, :, :3] if arr.shape[2] >= 3 else np.repeat(arr, 3, axis=2)
            if arr.dtype != np.uint8:
                arr = arr.astype(np.float32)
                arr = ((arr - arr.min()) / (arr.max() - arr.min() + 1e-6) * 255).astype(np.uint8)
        return Image.fromarray(arr)
    return Image.open(path).convert("RGB")

_vqa_processor = None
_vqa_model = None
_cap_processor = None
_cap_model = None


def load_vqa_models():
    global _vqa_processor, _vqa_model
    if _vqa_model is None:
        from peft import PeftModel
        from transformers import BlipForQuestionAnswering, BlipProcessor

        base = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base")
        _vqa_processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
        _vqa_model = PeftModel.from_pretrained(base, "outputs/vqa_adapter")
    return _vqa_processor, _vqa_model


def load_caption_models():
    global _cap_processor, _cap_model
    if _cap_model is None:
        from peft import PeftModel
        from transformers import BlipForConditionalGeneration, BlipProcessor

        base = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        _cap_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        _cap_model = PeftModel.from_pretrained(base, "outputs/caption_adapter")
    return _cap_processor, _cap_model

def run_vqa(image_path, query):
    img = load_image(image_path)
    processor, model = load_vqa_models()
    inputs = processor(img, query, return_tensors="pt")
    out = model.generate(**inputs, max_new_tokens=30)
    return processor.decode(out[0], skip_special_tokens=True)

def run_captioning(image_path, query):
    img = load_image(image_path)
    processor, model = load_caption_models()
    inputs = processor(img, return_tensors="pt")
    out = model.generate(**inputs, max_new_tokens=60)
    return processor.decode(out[0], skip_special_tokens=True)

def run_change_vqa(image1_path, image2_path, query):
    img1 = load_image(image1_path)
    img2 = load_image(image2_path)

    arr1, arr2 = np.array(img1), np.array(img2)
    diff = cv2.absdiff(arr1, arr2)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    cv2.imwrite("outputs/change_mask.png", thresh)
    change_ratio = np.count_nonzero(thresh) / thresh.size

    processor, model = load_caption_models()
    cap1_inputs = processor(img1, return_tensors="pt")
    cap2_inputs = processor(img2, return_tensors="pt")
    desc1 = processor.decode(model.generate(**cap1_inputs, max_new_tokens=40)[0], skip_special_tokens=True)
    desc2 = processor.decode(model.generate(**cap2_inputs, max_new_tokens=40)[0], skip_special_tokens=True)

    if change_ratio < 0.01:
        return f"No significant change detected. Before: {desc1}. After: {desc2}."
    else:
        return f"Change detected in approximately {change_ratio*100:.1f}% of the image. Before: {desc1}. After: {desc2}."


def find_band_file(folder: Path, required_band: str, extensions):
    for ext in extensions:
        for file in folder.rglob(f"*{required_band}*.{ext}"):
            if file.is_file():
                return file
    return None


def load_patch(s1_dir: Path, s2_dir: Path, model):
    from configilm.extra.BENv2_utils import STANDARD_BANDS, stack_and_interpolate

    channels = model.config.channels
    image_size = model.config.image_size

    if channels == 12:
        s2_bands = STANDARD_BANDS[10]
        s1_bands = STANDARD_BANDS[2]
        data = {}
        for band in s2_bands:
            file = find_band_file(s2_dir, band, ["jp2","tif", "tiff"])
            if file is None:
                raise FileNotFoundError(f"Missing S2 band {band} in {s2_dir}")
            with rasterio.open(file) as src:
                data[band] = src.read(1)
        for band in s1_bands:
            file = find_band_file(s1_dir, band, ["tif", "tiff"])
            if file is None:
                raise FileNotFoundError(f"Missing S1 band {band} in {s1_dir}")
            with rasterio.open(file) as src:
                data[band] = src.read(1)
        img = stack_and_interpolate(data, order=s2_bands + s1_bands, img_size=image_size, upsample_mode="nearest")
    else:
        raise ValueError(f"Unsupported model channel count: {channels}")

    return img.unsqueeze(0)



def run_cross_modal_fusion(s1_path, s2_path, query):
    import torch
    from configilm.extra.BENv2_utils import NEW_LABELS
    from reben_publication.BigEarthNetv2_0_ImageClassifier import BigEarthNetv2_0_ImageClassifier

    s1_dir = Path(s1_path)
    s2_dir = Path(s2_path)
    sar_classifier = BigEarthNetv2_0_ImageClassifier.from_pretrained("hackelle/resnet18-all-v0.1.1")
    sar_classifier.eval()

    with torch.no_grad():
        tensor = load_patch(s1_dir, s2_dir, sar_classifier)
        output = sar_classifier(tensor)
        probs = torch.sigmoid(output)[0]
        top_idx = torch.argmax(probs).item()
        predicted_class = NEW_LABELS[top_idx]
        confidence = probs[top_idx].item()
        
    return f"Optical-SAR classification result: '{predicted_class}' (confidence: {confidence:.2f}). Query context: {query}"