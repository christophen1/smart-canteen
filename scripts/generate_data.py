"""
校园食堂测试数据集生成脚本

用法:
    python scripts/generate_data.py

输出:
    scripts/data.sql — 可直接 source 执行的 SQL 文件

数据规模:
    user: 205 (200普通 + 5管理员)
    category: 5
    dish: 30
    orders: ~7000 (90天)
    order_item: ~12000
"""

import random
import uuid
from datetime import datetime, timedelta

random.seed(42)

OUTPUT = "scripts/data.sql"
DAYS = 90
START_DATE = datetime(2026, 1, 1)

# ============================================================
# 数据池
# ============================================================
SURNAMES = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜"
GIVEN = ["伟","芳","娜","敏","静","丽","强","磊","洋","艳","勇","军","杰","鑫","欣","慧","涛","明","超","秀英","文","华","浩","宇","辰","鑫","博","嘉","萱"]

CATEGORIES = [
    (1, "主食类"),
    (2, "炒菜类"),
    (3, "汤品类"),
    (4, "小吃类"),
    (5, "饮品类"),
]

DISHES = [
    # (category_id, name, price)
    # 主食类
    (1, "米饭套餐（两荤一素）", 15.00),
    (1, "红烧牛肉面", 14.00),
    (1, "蛋炒饭", 10.00),
    (1, "炸酱面", 12.00),
    (1, "扬州炒饭", 12.00),
    (1, "鸡蛋灌饼", 8.00),
    # 炒菜类
    (2, "鱼香肉丝", 16.00),
    (2, "宫保鸡丁", 16.00),
    (2, "番茄炒蛋", 10.00),
    (2, "糖醋里脊", 20.00),
    (2, "麻婆豆腐", 12.00),
    (2, "回锅肉", 18.00),
    (2, "红烧排骨", 22.00),
    (2, "干煸豆角", 10.00),
    (2, "蒜蓉西兰花", 10.00),
    # 汤品类
    (3, "紫菜蛋花汤", 5.00),
    (3, "番茄蛋汤", 6.00),
    (3, "酸辣汤", 8.00),
    (3, "排骨玉米汤", 12.00),
    (3, "菌菇鸡汤", 15.00),
    # 小吃类
    (4, "炸鸡腿", 8.00),
    (4, "春卷", 6.00),
    (4, "煎饺", 10.00),
    (4, "薯条", 8.00),
    (4, "烤肠", 5.00),
    (4, "鸡米花", 9.00),
    # 饮品类
    (5, "可乐", 4.00),
    (5, "柠檬水", 5.00),
    (5, "珍珠奶茶", 10.00),
    (5, "冰红茶", 5.00),
]

ADMIN_USERNAMES = ["admin1", "admin2", "admin3", "admin4", "admin5"]


def write(f, sql, *args):
    if args:
        f.write(sql % args)
    else:
        f.write(sql)
    f.write("\n")


def generate():
    users = []   # [(id, username, password_hash, role)]
    orders_ids = []  # [order_id]

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("-- Smart Canteen 测试数据集\n")
        f.write(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-- 数据范围: 2026-01-01 ~ 2026-03-31 (90天)\n\n")
        f.write("USE smart_canteen;\n\n")

        # ============================================================
        # 1. user
        # ============================================================
        f.write("-- ============================================\n")
        f.write("-- 用户数据 (200普通 + 5管理员)\n")
        f.write("-- ============================================\n")

        # BCrypt hash for "123456"
        pwd = "$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy"

        for i in range(1, 206):
            username = f"user{i:03d}" if i <= 200 else ADMIN_USERNAMES[i - 201]
            role = 0 if i <= 200 else 1
            real_name = random.choice(SURNAMES) + random.choice(GIVEN)
            phone = f"138{random.randint(10000000, 99999999)}"
            users.append((i, username, role))

            write(f, "INSERT INTO user (id, username, password, real_name, phone, role, status, create_time) VALUES")
            write(f, "(%d, '%s', '%s', '%s', '%s', %d, 1, '%s');",
                  i, username, pwd, real_name, phone, role,
                  START_DATE.strftime('%Y-%m-%d %H:%M:%S'))

        f.write("\n")

        # ============================================================
        # 2. category
        # ============================================================
        f.write("-- ============================================\n")
        f.write("-- 分类数据\n")
        f.write("-- ============================================\n")
        for sort_order, (cid, name) in enumerate(CATEGORIES, 1):
            write(f, "INSERT INTO category (id, name, sort) VALUES (%d, '%s', %d);",
                  cid, name, sort_order)
        f.write("\n")

        # ============================================================
        # 3. dish
        # ============================================================
        f.write("-- ============================================\n")
        f.write("-- 菜品数据 (%d个)\n" % len(DISHES))
        f.write("-- ============================================\n")
        for did, (cid, name, price) in enumerate(DISHES, 1):
            write(f, "INSERT INTO dish (id, category_id, name, price, status) VALUES (%d, %d, '%s', %.2f, 1);",
                  did, cid, name, price)
        f.write("\n")

        # ============================================================
        # 4. orders + order_item
        # ============================================================
        f.write("-- ============================================\n")
        f.write("-- 订单数据 (90天)\n")
        f.write("-- ============================================\n")

        order_id = 1

        for day_offset in range(DAYS):
            date = START_DATE + timedelta(days=day_offset)
            date_str = date.strftime('%Y-%m-%d')
            weekday = date.weekday()  # 0=Mon, 6=Sun

            # 周末订单量约为工作日的 60%
            if weekday < 5:
                daily_orders = random.randint(70, 100)
            else:
                daily_orders = random.randint(40, 60)

            for _ in range(daily_orders):
                # 高峰时段概率分布 — 午餐/晚餐集中
                hour_weights = [(h, 3 if h in (11, 12, 17, 18) else 2 if h in (10, 13, 16, 19) else 1)
                                for h in range(8, 21)]
                hours = [h for h, w in hour_weights for _ in range(w)]
                h = random.choice(hours)
                m = random.randint(0, 59)
                s = random.randint(0, 59)
                order_time = f"{date_str} {h:02d}:{m:02d}:{s:02d}"

                user = random.choice(users)
                user_id = user[0]

                # 每个订单 1-4 个菜品
                item_count = random.choices([1, 2, 3, 4], weights=[30, 40, 20, 10])[0]
                picked = random.sample(list(enumerate(DISHES, 1)), min(item_count, len(DISHES)))
                picked = picked[:item_count]

                total_amount = sum(dprice for _, (_, _, dprice) in picked)
                order_no = f"{date.strftime('%Y%m%d')}{uuid.uuid4().hex[:12].upper()}"

                # 状态分布: 大部分已完成，少量待支付/已取消
                status = random.choices([0, 1, 2, 3], weights=[5, 10, 15, 70])[0]

                write(f, "INSERT INTO orders (id, order_no, user_id, total_amount, status, create_time) VALUES")
                write(f, "(%d, '%s', %d, %.2f, %d, '%s');",
                      order_id, order_no, user_id, total_amount, status, order_time)

                for did, (_, dname, dprice) in picked:
                    qty = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
                    write(f, "INSERT INTO order_item (order_id, dish_id, dish_name, dish_price, quantity, create_time) VALUES")
                    write(f, "(%d, %d, '%s', %.2f, %d, '%s');",
                          order_id, did, dname, dprice, qty, order_time)

                orders_ids.append(order_id)
                order_id += 1

        f.write("\n")
        f.write(f"-- 总计: {order_id - 1} 个订单, {order_id - 1} 条 order_item\n")

    print(f"生成完成: {OUTPUT}")
    print(f"  用户: 205 (200普通 + 5管理员, 密码均为 123456)")
    print(f"  分类: {len(CATEGORIES)}")
    print(f"  菜品: {len(DISHES)}")
    print(f"  订单: {order_id - 1}")
    print(f"\n导入: mysql -u root -p < {OUTPUT}")


if __name__ == "__main__":
    generate()
