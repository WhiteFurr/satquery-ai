import rasterio
try:
    from .tasks import run_vqa, run_captioning, run_change_vqa, run_cross_modal_fusion
except ImportError:
    from tasks import run_vqa, run_captioning, run_change_vqa, run_cross_modal_fusion

def detect_modality(filepath):
    if not filepath.lower().endswith((".tif", ".tiff")):
        return "optical"
    with rasterio.open(filepath) as src:
        return "SAR" if src.count <= 2 else "optical"

def check_compatibility(image_list):
    issues = []
    tif_files = [f for f in image_list if f.lower().endswith((".tif", ".tiff"))]
    for img in tif_files:
        with rasterio.open(img) as src:
            if src.crs is None:
                issues.append(f"{img}: missing geographic reference")
    if len(tif_files) == 2:
        with rasterio.open(tif_files[0]) as a, rasterio.open(tif_files[1]) as b:
            if a.bounds != b.bounds:
                issues.append("Images do not cover the same geographic area")
    return issues

class CentralController:
    def route(self, query, image_list):
        issues = check_compatibility(image_list)
        if issues:
            return f"Cannot proceed: {issues}", [{"task": "compatibility_check", "result": "failed", "issues": issues}]

        if len(image_list) == 2:
            mod1, mod2 = detect_modality(image_list[0]), detect_modality(image_list[1])
            
            # Controller routing branch for multi-modal / SAR fusion
            if "sar" in query.lower() or mod1 != mod2:
                # Assuming image_list[0] or folders are structured accordingly. 
                # Pass your directory paths or file paths here based on how you upload them:
                result = run_cross_modal_fusion(image_list[0], image_list[1], query)
                log = [{"task": "cross_modal_fusion", "model": "BigEarthNetv2.0-ResNet18", "modalities": [mod1, mod2]}]
            else:
                result = run_change_vqa(image_list[0], image_list[1], query)
                log = [{"task": "change_vqa", "model": "BLIP-LoRA-adapted", "modalities": [mod1, mod2]}]
                
        elif "describe" in query.lower() or "caption" in query.lower():
            result = run_captioning(image_list[0], query)
            log = [{"task": "captioning", "model": "BLIP-captioning-LoRA"}]
        else:
            result = run_vqa(image_list[0], query)
            log = [{"task": "single_image_vqa", "model": "BLIP-LoRA-adapted"}]

        return result, log