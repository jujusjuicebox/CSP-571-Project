# pip install opencv-python tqdm
import cv2, math, sys
from pathlib import Path
from tqdm import tqdm

VIDEO_EXTS = {".mp4", ".avi", ".mkv", ".mov", ".m4v"}

def extract_frames_for_video(
    video_path: Path,
    target_fps: float | None = None,
    img_ext: str = ".jpg",
    quality: int = 95,
    prefix: str = "frame_",
    start_sec: float = 0.0,
    end_sec: float | None = None
) -> int:
    out_dir = video_path.with_suffix("")
    out_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"[WARN] Could not open {video_path}")
        return 0

    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    start_frame = int(max(0, start_sec * src_fps))
    end_frame = total_frames if end_sec is None else int(min(end_sec * src_fps, total_frames))

    stride = 1
    if target_fps and target_fps > 0:
        stride = max(1, math.floor(src_fps / target_fps))

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    current = start_frame
    saved = 0

    # Progress estimation
    steps = 0
    if end_frame and end_frame > start_frame:
        steps = (end_frame - start_frame + stride - 1) // stride

    pbar = tqdm(total=steps, desc=f"{video_path.name}", unit="frame")
    while True:
        if end_frame and current >= end_frame:
            break
        ret, frame = cap.read()
        if not ret:
            break

        if (current - start_frame) % stride == 0:
            name = f"{prefix}{saved:06d}{img_ext}"
            out_path = out_dir / name

            if img_ext.lower() == ".jpg":
                cv2.imwrite(str(out_path), frame, [cv2.IMWRITE_JPEG_QUALITY, int(quality)])
            elif img_ext.lower() == ".png":
                comp = max(0, min(9, 9 - int(round((quality / 100) * 9))))
                cv2.imwrite(str(out_path), frame, [cv2.IMWRITE_PNG_COMPRESSION, comp])
            else:
                cv2.imwrite(str(out_path), frame)

            saved += 1
            pbar.update(1)

        current += 1

    pbar.close()
    cap.release()
    print(f"[OK] {video_path.name}: saved {saved} frames to {out_dir}")
    return saved

def extract_frames_in_folder(
    root: str | Path,
    recursive: bool = False,
    target_fps: float | None = None,
    img_ext: str = ".jpg",
    quality: int = 95,
    prefix: str = "frame_",
    start_sec: float = 0.0,
    end_sec: float | None = None,
):
    root = Path(root)
    if not root.exists():
        print(f"[ERR] Folder not found: {root}")
        return

    pattern = "**/*" if recursive else "*"
    videos = [p for p in root.glob(pattern) if p.is_file() and p.suffix.lower() in VIDEO_EXTS]
    if not videos:
        print("[INFO] No videos found.")
        return

    print(f"[INFO] Found {len(videos)} videos in {root} (recursive={recursive})")
    total_saved = 0
    for vid in videos:
        total_saved += extract_frames_for_video(
            vid, target_fps=target_fps, img_ext=img_ext, quality=quality,
            prefix=prefix, start_sec=start_sec, end_sec=end_sec
        )
    print(f"[DONE] Total frames saved: {total_saved}")

if __name__ == "__main__":
    folder = Path("/Users/amoghjadhav/Documents/Data Preparation and Analysis/Project/chute04")
    extract_frames_in_folder(
        root=folder,
        recursive=False,
        target_fps=None,     # change the frames per second over here if you keep it as 5 then it wil take 5 frames every second and store them 
        img_ext=".jpg",
        quality=95,
        prefix="frame_",
        start_sec=0.0,
        end_sec=None
    )
