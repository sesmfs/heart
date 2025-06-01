"""
这是一个生成爱心动画的程序
使用贝塞尔曲线绘制爱心形状，并添加粒子效果使其更加动态和美观
作者: 小树学AI
"""

import cv2
import numpy as np
import os

def lerp(a, b, t):
    """在两个值之间平滑过渡"""
    return a * (1 - t) + b * t

def bezier(points, t):
    """计算贝塞尔曲线上的点"""
    if len(points) == 1:
        return points[0]
    points = np.stack(points)
    next_points = [lerp(points[i], points[i+1], t) for i in range(len(points)-1)]
    return bezier(next_points, t)

def create_heart_points(points, num_points=150):
    """生成心形轮廓点集"""
    heart = []
    for t in np.linspace(0, 1, num_points):
        p = bezier(points, t)
        heart.append(p)
        # 对称生成另一半
        heart.append([2 * points[0][0] - p[0], p[1]])
    return np.stack(heart)

# 画布设置
WIDTH, HEIGHT = 1024, 680
CENTER = np.array([WIDTH, HEIGHT]).reshape(-1, 2) / 2

# 心形控制点
BASE_HEART = np.array([
    [512.0, 204.0],  # 顶部中心
    (421, 9),        # 左上
    (99, 209),       # 左侧
    (376, 358),      # 左下
    (420, 493),      # 底部
    [512.0, 544.0]   # 底部中心
]) - [WIDTH/2, HEIGHT/2]

FINAL_HEART = np.array([
    [512.0, 146],    # 顶部中心
    (420, -18),      # 左上
    (82, 202),       # 左侧
    (292, 363),      # 左下
    (362, 524),      # 底部
    [512.0, 566]     # 底部中心
]) - [WIDTH/2, HEIGHT/2]

# 生成各状态的心形
tiny_heart = create_heart_points(BASE_HEART * 0.01)   # 最小
small_heart = create_heart_points(BASE_HEART * 0.35)  # 中等
base_heart = create_heart_points(BASE_HEART)          # 初始
final_heart = create_heart_points(FINAL_HEART * 0.9)  # 最终

# 动画过渡权重
weights = []
for t in np.linspace(0, 1, 70):
    weights.append(bezier(np.array([
        [0, 0],
        [.0,.82],
        [0.14,0.99],
        [1, 1]
    ]), t)[1])
weights = (1-np.stack(weights))[::-1]

# 粒子颜色
COLOR_HEART_BRIGHT = np.array([22, 5, 255])       # 爱心红色
COLOR_HEART_DARK = np.array([189, 172, 245])      # 爱心粉色
COLOR_DECOR_BRIGHT = np.array([22, 5, 255])      # 装饰粒子红色
COLOR_DECOR_DARK = np.array([255, 198, 255])     # 装饰粒子粉色

def create_heart_particles(current, t):
    """生成爱心粒子"""
    result = []
    for rc in np.linspace(1, 0.0, 180):
        count = max(0, int(rc ** 2.8 * len(tiny_heart)))
        idx = np.random.choice(np.arange(len(tiny_heart)), size=count)
        
        for p1, p2, p3, p4 in zip(tiny_heart[idx], small_heart[idx], 
                                 base_heart[idx], current[idx]):
            rand = (np.random.rand(2) * 2 - 1) * 30 * (1 - rc*0.90)
            pos1 = lerp(p1, p4, rc) + rand
            pos2 = lerp(p2, p4, rc)
            result.append(lerp(pos1, pos2, t * min(1.0, rc / 0.05)))
    
    return np.stack(result)

def create_decor_particles(frame_idx, t):
    """生成装饰粒子"""
    result = []
    np.random.seed(frame_idx // 5)
    
    for rc in np.linspace(1, 0.0, 150):
        count = int(np.random.rand() * rc * len(tiny_heart))
        idx = np.random.choice(np.arange(len(tiny_heart)), size=count)
        
        for p1, p2 in zip(tiny_heart[idx], final_heart[idx]*1.35):
            rand_a = (np.random.randn() * 0.8) * (1 - t) * 0.1 + 0.9
            pos = lerp(p1, p2, rand_a * rc * (0.9 + (1-t) * 0.15))
            pos += (np.random.rand(2) * 2 - 1) * 30
            result.append((pos, np.random.rand()))
    
    return result

def main():
    """运行爱心动画"""
    # 创建输出目录
    os.makedirs("imgs", exist_ok=True)

    # 创建画布
    canvas = np.zeros((HEIGHT, WIDTH, 3), np.uint8)

    # 生成动画
    for frame_idx, t in enumerate(weights):
        canvas[:] = 0
        np.random.seed(3)
        
        # 计算当前状态
        current = lerp(base_heart, final_heart, t)
        
        # 生成爱心
        particles = create_heart_particles(current, t)
        particles = ((particles + CENTER) * 16).astype(np.int32)
        
        # 绘制爱心
        for x, y in particles:
            size = int(np.random.rand() * 1.1 * 16)
            color_t = (1 - np.cos(np.random.rand() * np.pi)) / 2
            color = lerp(COLOR_HEART_BRIGHT, COLOR_HEART_DARK, color_t)
            cv2.circle(canvas, (x, y), size, color, -1, 16, shift=4)

        # 生成和绘制装饰粒子
        for pos, rand_t in create_decor_particles(frame_idx, t):
            x, y = ((pos + CENTER[0]) * 16).astype(np.int32)
            size = int(np.random.rand() * 1 * 16)
            color = lerp(COLOR_DECOR_BRIGHT, COLOR_DECOR_DARK, rand_t)
            cv2.circle(canvas, (x, y), size, color, -1, 16, shift=4)

        # 显示和保存
        cv2.imshow("Heart", canvas)
        cv2.imwrite(f"imgs/{frame_idx:05d}.jpg", canvas)
        
        # 显示保存进度
        progress = (frame_idx + 1) / len(weights) * 100
        print(f"\r保存进度: {progress:.1f}% ({frame_idx + 1}/{len(weights)}帧)", end="")
        
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    print("\n所有图片保存完成")

if __name__ == "__main__":
    main()