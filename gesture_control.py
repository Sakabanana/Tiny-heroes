import cv2
import mediapipe as mp
import pygame
import numpy as np

class GestureController:
    def __init__(self):

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)
        
        # 动作状态
        self.actions = {
            "move_left": False,
            "move_right": False,
            "move_up": False,
            "move_down": False,
            "melee": False,
            "shoot": False
        }
        
        self.current_status_text = ""
        # 详细状态信息
        self.detected_hands = []  # 检测到的手：["L", "R"]
        self.left_hand_attack = "近战"  # 左手攻击状态：近战/远程
        self.right_hand_movement = ""  # 右手运动方向：上/下/左/右
        
        # 为左右手定义与界面显示一致的颜色
        self.left_hand_color = (0, 255, 255)      # 黄色 - 近战/远程攻击 (BGR格式)
        self.right_hand_color = (255, 150, 50)    # 蓝色 - 移动 (BGR格式)

    def process_frame(self):
        if not self.cap.isOpened():
            print("Error: Camera is not opened.")  # 添加调试信息
            return None, self.actions

        success, image = self.cap.read()
        if not success:
            print("Error: Failed to read frame from camera.")  # 添加调试信息
            return None, self.actions

        # 翻转图像，使其像镜子一样
        image = cv2.flip(image, 1)
        
        # 转换颜色空间 BGR -> RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 处理图像
        results = self.hands.process(image_rgb)
        
        # 重置动作和状态
        self.actions = {k: False for k in self.actions}
        self.current_status_text = ""
        self.detected_hands = []
        self.left_hand_attack = "近战"  # 默认近战
        self.right_hand_movement = ""  # 默认无运动
        
        left_hand_present = False
        right_hand_present = False
        
        # 先绘制骨架再处理手势逻辑
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                label = handedness.classification[0].label
                
                # 根据左右手使用不同颜色绘制骨骼
                if label == "Left":
                    hand_color = self.left_hand_color
                    left_hand_present = True
                    self.detected_hands.append("L")
                    # 左手出现时改为远程攻击
                    self.actions["shoot"] = True
                    self.left_hand_attack = "远程"
                else:  # Right
                    hand_color = self.right_hand_color
                    right_hand_present = True
                    self.detected_hands.append("R")
                    wrist = hand_landmarks.landmark[0]
                    x, y = wrist.x, wrist.y
                    
                    # 检测运动方向（只识别单一方向）
                    movement_dir = ""
                    # 先检查主要方向（水平 vs 垂直）
                    if abs(x - 0.5) > abs(y - 0.5):
                        # 水平方向为主
                        if x < 0.4:
                            self.actions["move_left"] = True
                            movement_dir = "左"
                        elif x > 0.6:
                            self.actions["move_right"] = True
                            movement_dir = "右"
                    else:
                        # 垂直方向为主
                        if y < 0.4:
                            self.actions["move_up"] = True
                            movement_dir = "上"
                        elif y > 0.6:
                            self.actions["move_down"] = True
                            movement_dir = "下"
                    
                    # 更新右手运动状态
                    self.right_hand_movement = movement_dir if movement_dir else "无"
                
                # 绘制骨骼，使用对应的颜色
                self.mp_draw.draw_landmarks(
                    image, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=self.mp_draw.DrawingSpec(color=hand_color, thickness=2, circle_radius=2),
                    connection_drawing_spec=self.mp_draw.DrawingSpec(color=hand_color, thickness=2)
                )

        # 左手未出现时，保持近战状态
        if not left_hand_present:
            self.actions["melee"] = True
            self.left_hand_attack = "近战"
        
        return image, self.actions

    def get_pygame_image(self, image):
        if image is None:
            return None
        try:
            # 转换 opencv 图像 (BGR) 到 pygame surface (RGB)
            # OpenCV 图像是 BGR 格式，需要转换为 RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 使用 pygame.image.frombuffer 是最简单可靠的方法
            # 参数：bytes数据, 尺寸(width, height), 格式
            return pygame.image.frombuffer(image_rgb.tobytes(), image_rgb.shape[1::-1], "RGB")
        except Exception as e:
            print(f"Error converting image to pygame surface: {e}")
            import traceback
            traceback.print_exc()
            return None

    def release(self):
        self.cap.release()