from PIL import Image
import os

def get_reference_size(input_dir, reference_image):
    """
    기준 이미지의 크기를 반환합니다.
    
    Args:
        input_dir (str): 이미지가 있는 디렉토리 경로
        reference_image (str): 기준 이미지 파일명
    
    Returns:
        tuple: (width, height) 기준 이미지의 크기
    """
    reference_path = os.path.join(input_dir, reference_image)
    if not os.path.exists(reference_path):
        raise FileNotFoundError(f"기준 이미지 {reference_image}를 찾을 수 없습니다.")
    
    with Image.open(reference_path) as img:
        return img.size

def resize_image_with_ratio(img, target_width, target_height):
    """
    이미지의 가로세로 비율을 유지하면서 크기를 조정하고 중앙에서 잘라냅니다.
    
    Args:
        img (PIL.Image): 원본 이미지
        target_width (int): 목표 너비
        target_height (int): 목표 높이
    
    Returns:
        PIL.Image: 처리된 이미지
    """
    # 원본 이미지의 비율
    original_ratio = img.width / img.height
    
    # 목표 비율
    target_ratio = target_width / target_height
    
    if original_ratio > target_ratio:
        # 이미지가 더 넓은 경우
        new_width = int(target_height * original_ratio)
        new_height = target_height
        # 중앙에서 잘라내기
        left = (new_width - target_width) // 2
        top = 0
        right = left + target_width
        bottom = target_height
    else:
        # 이미지가 더 좁은 경우
        new_width = target_width
        new_height = int(target_width / original_ratio)
        # 중앙에서 잘라내기
        left = 0
        top = (new_height - target_height) // 2
        right = target_width
        bottom = top + target_height
    
    # 이미지 리사이즈
    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # 중앙에서 잘라내기
    return resized_img.crop((left, top, right, bottom))

def resize_images(input_dir, output_dir, reference_image="gaenari.jpg"):
    """
    입력 디렉토리의 모든 이미지를 기준 이미지 크기로 리사이즈하여 출력 디렉토리에 저장합니다.
    
    Args:
        input_dir (str): 원본 이미지가 있는 디렉토리 경로
        output_dir (str): 리사이즈된 이미지를 저장할 디렉토리 경로
        reference_image (str): 기준 이미지 파일명
    """
    # 출력 디렉토리가 없으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 기준 이미지 크기 가져오기
    target_width, target_height = get_reference_size(input_dir, reference_image)
    print(f"목표 크기: {target_width}x{target_height}")
    
    # 지원하는 이미지 확장자
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    
    # 입력 디렉토리의 모든 파일 처리
    for filename in os.listdir(input_dir):
        if not any(filename.lower().endswith(ext) for ext in valid_extensions):
            continue
            
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        try:
            # 이미지 열기
            with Image.open(input_path) as img:
                # 이미지 크기 조정
                processed_img = resize_image_with_ratio(img, target_width, target_height)
                
                # 이미지 저장
                processed_img.save(output_path, quality=95)
                print(f"처리 완료: {filename}")
                
        except Exception as e:
            print(f"오류 발생 ({filename}): {str(e)}")

if __name__ == "__main__":
    # 입력 및 출력 디렉토리 설정
    input_directory = "images"  # 원본 이미지 폴더
    output_directory = "images_resized"  # 리사이즈된 이미지 저장 폴더
    
    # 이미지 리사이즈 실행
    resize_images(input_directory, output_directory)
    print("모든 이미지 처리 완료!")
