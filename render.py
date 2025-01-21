import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from pathlib import Path
import torch
import argparse
import os
import cv2
import numpy as np
from hmr2.configs import CACHE_DIR_4DHUMANS
from hmr2.models import HMR2, download_models, load_hmr2, DEFAULT_CHECKPOINT
from hmr2.utils import recursive_to
from hmr2.datasets.vitdet_dataset import ViTDetDataset
from hmr2.utils.renderer import Renderer, cam_crop_to_full

# Color for the mesh (optional customization)
LIGHT_BLUE = (0.65098039, 0.74117647, 0.85882353)


def warm_up():
    """Warm-up function to initialize models and detectors."""
    # Download and load checkpoints
    download_models(CACHE_DIR_4DHUMANS)
    model, model_cfg = load_hmr2(DEFAULT_CHECKPOINT)

    # Set device
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    model = model.to(device)
    model.eval()

    # Load detector
    from hmr2.utils.utils_detectron2 import DefaultPredictor_Lazy
    from detectron2.config import LazyConfig
    import hmr2
    cfg_path = Path(hmr2.__file__).parent / 'configs' / 'cascade_mask_rcnn_vitdet_h_75ep.py'
    detectron2_cfg = LazyConfig.load(str(cfg_path))
    detectron2_cfg.train.init_checkpoint = "https://dl.fbaipublicfiles.com/detectron2/ViTDet/COCO/cascade_mask_rcnn_vitdet_h/f328730692/model_final_f05665.pkl"
    for i in range(3):
        detectron2_cfg.model.roi_heads.box_predictors[i].test_score_thresh = 0.25
    detector = DefaultPredictor_Lazy(detectron2_cfg)

    print("Warm-up complete.")
    return model, detector, model_cfg


def main():
    parser = argparse.ArgumentParser(description='HMR2 demo code')
    parser.add_argument('--checkpoint', type=str, default=DEFAULT_CHECKPOINT, help='Path to pretrained model checkpoint')
    parser.add_argument('--img_folder', type=str, default='example_data/images', help='Folder with input images')
    parser.add_argument('--out_folder', type=str, default='demo_out', help='Output folder to save meshes')
    parser.add_argument('--batch_size', type=int, default=1, help='Batch size for inference/fitting')
    parser.add_argument('--file_type', nargs='+', default=['*.jpg', '*.png'], help='List of file extensions to consider')

    args = parser.parse_args()

    # Warm-up and initialize
    model, detector, model_cfg = warm_up()
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    # Initialize the renderer
    renderer = Renderer(model_cfg, faces=model.smpl.faces)

    # Make output directory if it does not exist
    os.makedirs(args.out_folder, exist_ok=True)

    # Get all demo images that end with specified extensions
    img_paths = [img for ext in args.file_type for img in Path(args.img_folder).glob(ext)]

    # Iterate over all images in the folder
    counter = 0
    for img_path in img_paths:
        img_cv2 = cv2.imread(str(img_path))

        # Detect humans in image
        det_out = detector(img_cv2)
        det_instances = det_out['instances']
        valid_idx = (det_instances.pred_classes == 0) & (det_instances.scores > 0.5)
        boxes = det_instances.pred_boxes.tensor[valid_idx].cpu().numpy()

        # Run HMR2.0 on all detected humans
        dataset = ViTDetDataset(model_cfg, img_cv2, boxes)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)

        for batch in dataloader:
            batch = recursive_to(batch, device)
            with torch.no_grad():
                out = model(batch)

            pred_cam = out['pred_cam']
            box_center = batch["box_center"].float()
            box_size = batch["box_size"].float()
            img_size = batch["img_size"].float()
            scaled_focal_length = model_cfg.EXTRA.FOCAL_LENGTH / model_cfg.MODEL.IMAGE_SIZE * img_size.max()
            pred_cam_t_full = cam_crop_to_full(pred_cam, box_center, box_size, img_size, scaled_focal_length).detach().cpu().numpy()

            batch_size = batch['img'].shape[0]
            for n in range(batch_size):
                img_fn, _ = os.path.splitext(os.path.basename(img_path))
                person_id = int(batch['personid'][n])

                # Save mesh to disk
                verts = out['pred_vertices'][n].detach().cpu().numpy()
                cam_t = pred_cam_t_full[n]
                camera_translation = cam_t.copy()
                tmesh = renderer.vertices_to_trimesh(verts, camera_translation, LIGHT_BLUE)
                tmesh.export(os.path.join(args.out_folder, f'pose{counter}.obj'))
        
        counter += 1


if __name__ == '__main__':
    main()
