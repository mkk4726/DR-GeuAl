import os
import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from assets.one_mask.Preprocessing import preprocess_image
from assets.one_mask.models import SMD_Unet

def load_and_resize_images(image_path, use_3channel=True, use_hist=False):
    image = preprocess_image(image_path, 
                            img_size=(512, 512), 
                            use_3channel=use_3channel,
                            use_hist=use_hist)
    return image

def apply_color_to_mask(mask, color):
    # 마스크의 흰색 영역을 해당 색으로 변경
    colored_mask = np.zeros((*mask.shape[:2], 3), dtype=np.uint8)
    indices = np.where(mask)
    for i in range(len(indices[0])):
        row, col = indices[0][i], indices[1][i]
        colored_mask[row, col] = color
    return colored_mask

def combine_masks(mask_ex, mask_he, mask_ma, mask_se):
    # 각 마스크를 색상으로 변환
    mask_ex_color = apply_color_to_mask(mask_ex, [255, 0, 0])  # 빨간색
    mask_he_color = apply_color_to_mask(mask_he, [0, 0, 255])  # 파란색
    mask_ma_color = apply_color_to_mask(mask_ma, [255, 255, 0])  # 노란색
    mask_se_color = apply_color_to_mask(mask_se, [0, 255, 0])  # 초록색

    # 색상별 마스크를 합치기
    combined_mask = mask_ex_color + mask_he_color + mask_ma_color + mask_se_color
    combined_mask[combined_mask > 255] = 255  # 최대값을 255로 제한
    return combined_mask

def visualize_segmentation(image, mask_ex, mask_he, mask_ma, mask_se, mask_true, mask_pred):
    plt.figure(figsize=(18, 12))

    # 원본 이미지
    plt.subplot(2, 5, 1)
    # 이미지 데이터를 0에서 255 사이의 정수 값으로 스케일링
    scaled_image = (image * 255).astype(np.uint8)
    # 이미지의 채널 순서 변경 (BGR -> RGB)
    rgb_image = cv2.cvtColor(scaled_image, cv2.COLOR_BGR2RGB)
    plt.imshow(rgb_image)
    plt.title('Original Image')
    plt.axis('off')

    # Ex 마스크 출력 (빨간색)
    plt.subplot(2, 5, 2)
    mask_ex_color = apply_color_to_mask(mask_ex, [255, 0, 0])  # 빨간색
    plt.imshow(mask_ex_color)
    plt.title('Ex Mask\n{}'.format(os.path.basename(os.path.join(mask_paths[0], image_filename))))
    plt.title('Ex Mask')
    plt.axis('off')

    # He 마스크 출력 (파란색)
    plt.subplot(2, 5, 3)
    mask_he_color = apply_color_to_mask(mask_he, [0, 0, 255])  # 파란색
    plt.imshow(mask_he_color)
    plt.title('He Mask')
    plt.axis('off')

    # Ma 마스크 출력 (노란색)
    plt.subplot(2, 5, 4)
    mask_ma_color = apply_color_to_mask(mask_ma, [255, 255, 0])  # 노란색
    plt.imshow(mask_ma_color)
    plt.title('Ma Mask')
    plt.axis('off')

    # Se 마스크 출력 (초록색)
    plt.subplot(2, 5, 5)
    mask_se_color = apply_color_to_mask(mask_se, [0, 255, 0])  # 초록색
    plt.imshow(mask_se_color)
    plt.title('Se Mask')
    plt.axis('off')

    plt.tight_layout()

    # Target 및 Predicted 마스크
    plt.figure(figsize=(10, 5))

    # 실제 세그멘테이션 마스크 출력 (Target 마스크)
    mask_target_combined = combine_masks(mask_ex, mask_he, mask_ma, mask_se)
    plt.subplot(1, 2, 1)
    plt.imshow(mask_target_combined)
    plt.title('Target Mask')
    plt.axis('off')

    # 예측된 세그멘테이션 마스크 출력
    plt.subplot(1, 2, 2)
    plt.imshow(tf.squeeze(mask_pred), cmap='gray')  # tf.squeeze() 함수 적용
    plt.title('Predicted Mask')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

def visualize_segmentation_results(image_filenames, model_path):
    mask_dir = '../data/Seg-set'
    image_dir = '../data/Seg-set/Original_Images/'
    masks = ['HardExudate_Masks', 'Hemohedge_Masks', 'Microaneurysms_Masks', 'SoftExudate_Masks']
    mask_paths = [os.path.join(mask_dir, mask) for mask in masks]

    # 이미지 파일들을 정렬하여 가져옴
    image_files = sorted(os.listdir(image_dir))

    model = SMD_Unet(enc_filters=[64, 128, 256, 512, 1024], dec_filters=[512, 256, 64, 32], input_channel=3)
    model.load_weights(model_path)


    for image_filename in image_filenames:
        # 이미지 파일의 인덱스 가져오기
        image_index = image_files.index(image_filename)

        # 시각화할 원본 마스크 선택 및 리사이징
        selected_ex_mask = cv2.imread(os.path.join(mask_paths[0], image_filename), cv2.IMREAD_UNCHANGED)
        selected_ex_mask = cv2.resize(selected_ex_mask, (512, 512))

        selected_he_mask = cv2.imread(os.path.join(mask_paths[1], image_filename), cv2.IMREAD_UNCHANGED)
        selected_he_mask = cv2.resize(selected_he_mask, (512, 512))

        selected_ma_mask = cv2.imread(os.path.join(mask_paths[2], image_filename), cv2.IMREAD_UNCHANGED)
        selected_ma_mask = cv2.resize(selected_ma_mask, (512, 512))

        selected_se_mask = cv2.imread(os.path.join(mask_paths[3], image_filename), cv2.IMREAD_UNCHANGED)
        selected_se_mask = cv2.resize(selected_se_mask, (512, 512))

        # 이미지 파일의 경로
        image_path = os.path.join(image_dir, image_filename)

        # 이미지 로드 및 전처리
        image = load_and_resize_images(image_path, use_3channel=True, use_hist=False)

        # 모델에 이미지 전달하여 예측
        preds = model(image[np.newaxis, ...])

        # 시각화 함수 호출
        visualize_segmentation(image, selected_ex_mask, selected_he_mask, selected_ma_mask, selected_se_mask, None, preds[1])

if __name__ == "__main__":
    image_filenames = ["0381_1.png", "0311_1.png", "1134_1.png", "1181_3.png"]  # 원하는 이미지 파일명으로 수정
    model_path = "../models/one_mask/withoutCLAHE_withRecons_alpha01_lr00001_3channel/26"
    visualize_segmentation_results(image_filenames, model_path)
