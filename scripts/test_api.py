"""
Smart Canteen API 全接口测试脚本

用法:
    pip install requests
    python scripts/test_api.py

前提: SpringBoot 已启动，数据库已建表
"""

import requests
import json
import sys

BASE = "http://localhost:8080"

PASS = 0
FAIL = 0


def log(msg):
    print(f"  {msg}")


def ok(msg):
    global PASS
    PASS += 1
    print(f"  [PASS] {msg}")


def bad(msg, resp=None):
    global FAIL
    FAIL += 1
    print(f"  [FAIL] {msg}")
    if resp is not None:
        print(f"         status={resp.status_code} body={resp.text[:300]}")


def heading(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def api(method, path, token=None, **kwargs):
    url = f"{BASE}{path}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if method == "GET":
        return requests.get(url, headers=headers, **kwargs)
    elif method == "POST":
        return requests.post(url, headers=headers, **kwargs)
    elif method == "PUT":
        return requests.put(url, headers=headers, **kwargs)
    elif method == "DELETE":
        return requests.delete(url, headers=headers, **kwargs)


def assert_ok(resp, step_name):
    if resp.status_code == 200:
        body = resp.json()
        if body.get("code") == 200:
            ok(step_name)
            return body.get("data")
        else:
            bad(f"{step_name} — code={body.get('code')} msg={body.get('message')}")
    else:
        bad(f"{step_name} — HTTP {resp.status_code}")
    return None


def assert_fail(resp, step_name):
    """期望返回非200"""
    if resp.status_code != 200:
        ok(step_name)
        return True
    body = resp.json()
    if body.get("code") != 200:
        ok(f"{step_name} — got code={body.get('code')}")
        return True
    bad(f"{step_name} — 应失败却成功了")
    return False


# ============================================================
def test_user_flow():
    heading("1. 用户注册与登录")

    # 1.1 注册
    log("注册普通用户 testuser")
    resp = api("POST", "/api/user/register", json={
        "username": "testuser", "password": "123456"
    })
    assert_ok(resp, "注册 testuser")

    # 1.2 重复注册
    log("重复注册应失败")
    resp = api("POST", "/api/user/register", json={
        "username": "testuser", "password": "123456"
    })
    assert_fail(resp, "重复注册被拒绝")

    # 1.3 登录
    log("登录获取 token")
    resp = api("POST", "/api/user/login", json={
        "username": "testuser", "password": "123456"
    })
    data = assert_ok(resp, "登录成功")
    if data is None:
        return None
    token = data.get("token")
    ok(f"拿到 token: {token[:30]}...")
    return token


def test_admin_flow():
    heading("2. 管理员注册与登录")

    log("注册管理员 adminuser")
    resp = api("POST", "/api/user/register", json={
        "username": "adminuser", "password": "admin123"
    })
    body = resp.json()
    if body.get("code") == 200:
        ok("注册 adminuser 成功")
    else:
        log(f"adminuser 可能已存在: {body.get('message')}")

    log("自动将 adminuser 设为管理员")
    import subprocess
    mysql_exe = "C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysql.exe"
    cmd = f'"{mysql_exe}" -u root --password="!yzj20050626" smart_canteen -e "UPDATE user SET role = 1 WHERE username = \'adminuser\';"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        ok("adminuser 已设为管理员")
    else:
        bad(f"设置管理员失败: {result.stderr}")

    resp = api("POST", "/api/user/login", json={
        "username": "adminuser", "password": "admin123"
    })
    data = assert_ok(resp, "管理员登录")
    if data is None:
        return None
    token = data.get("token")
    ok(f"管理员 token: {token[:30]}...")
    return token


def test_category_crud(admin_token):
    heading("3. 分类管理 (管理员)")

    # 创建
    log("创建分类「主食类」")
    resp = api("POST", "/api/admin/category", token=admin_token, json={
        "name": "主食类", "sort": 1
    })
    assert_ok(resp, "创建分类")
    cat_id = None
    # 从 list 中取（POST 不返回 data，需从列表获取）
    resp = api("GET", "/api/category/list")
    data = assert_ok(resp, "获取分类列表")
    if data and len(data) > 0:
        # 取最后一个（最新创建的）
        cat_id = data[-1]["id"]
        ok(f"分类 ID = {cat_id}")

    log("创建分类「炒菜类」")
    api("POST", "/api/admin/category", token=admin_token, json={
        "name": "炒菜类", "sort": 2
    })
    log("创建分类「饮品类」")
    api("POST", "/api/admin/category", token=admin_token, json={
        "name": "饮品类", "sort": 3
    })

    # 修改
    log("修改分类名")
    resp = api("PUT", "/api/admin/category", token=admin_token, json={
        "id": cat_id, "name": "主食类(改)", "sort": 1
    })
    assert_ok(resp, "修改分类")

    # 列表
    resp = api("GET", "/api/category/list")
    data = assert_ok(resp, "查看分类列表")
    if data:
        ok(f"共 {len(data)} 个分类")

    return cat_id, admin_token


def test_dish_crud(admin_token, cat_id):
    heading("4. 菜品管理 (管理员)")

    if cat_id is None:
        bad("无分类ID，跳过菜品测试")
        return None, None

    dish_ids = []
    dishes = [
        {"name": "鱼香肉丝", "price": 15.0, "categoryId": cat_id, "description": "经典川菜"},
        {"name": "宫保鸡丁", "price": 16.0, "categoryId": cat_id, "description": "花生鸡丁"},
        {"name": "番茄炒蛋", "price": 10.0, "categoryId": cat_id, "description": "家常菜"},
    ]
    for d in dishes:
        log(f"创建菜品「{d['name']}」")
        resp = api("POST", "/api/admin/dish", token=admin_token, json=d)
        assert_ok(resp, f"创建 {d['name']}")

    # 查列表
    resp = api("GET", "/api/dish/page")
    data = assert_ok(resp, "查询菜品列表")
    if data and data.get("records"):
        for r in data["records"]:
            dish_ids.append(r["id"])
        ok(f"菜品列表共 {data['total']} 条")

    # 查详情
    if dish_ids:
        resp = api("GET", f"/api/dish/{dish_ids[0]}")
        data = assert_ok(resp, f"查看菜品详情 id={dish_ids[0]}")
        if data:
            ok(f"  菜品名: {data.get('name')}  价格: {data.get('price')}  分类: {data.get('categoryName')}")

    # 修改
    if dish_ids:
        log("修改菜品价格")
        resp = api("PUT", "/api/admin/dish", token=admin_token, json={
            "id": dish_ids[0], "name": "鱼香肉丝", "price": 17.0,
            "categoryId": cat_id, "description": "经典川菜，特制酱料"
        })
        assert_ok(resp, "修改菜品")

    # 上下架
    if dish_ids:
        log("下架菜品")
        resp = api("PUT", "/api/admin/dish/status", token=admin_token, json={
            "id": dish_ids[1], "status": 0
        })
        assert_ok(resp, "下架宫保鸡丁")

        log("上架菜品")
        resp = api("PUT", "/api/admin/dish/status", token=admin_token, json={
            "id": dish_ids[1], "status": 1
        })
        assert_ok(resp, "上架宫保鸡丁")

    return dish_ids[0] if dish_ids else None, dish_ids


def test_order_flow(user_token, dish_id):
    heading("5. 订单流程 (用户端)")

    if user_token is None or dish_id is None:
        bad("缺少 token 或菜品，跳过订单测试")
        return None

    # 下单
    log("提交订单")
    resp = api("POST", "/api/order", token=user_token, json={
        "items": [{"dishId": dish_id, "quantity": 2}],
        "remark": "少辣"
    })
    assert_ok(resp, "提交订单")

    # 再下一单
    log("再下一单")
    resp = api("POST", "/api/order", token=user_token, json={
        "items": [{"dishId": dish_id, "quantity": 1}],
        "remark": ""
    })
    assert_ok(resp, "再次提交订单")

    # 查我的订单
    resp = api("GET", "/api/order/page?page=1&size=10", token=user_token)
    data = assert_ok(resp, "查看我的订单")
    order_id = None
    if data and data.get("records"):
        order = data["records"][0]
        order_id = order["id"]
        ok(f"共 {data['total']} 个订单, 第一单金额={order['totalAmount']}, 状态={order['status']}")
        if order.get("items"):
            ok(f"  订单包含 {len(order['items'])} 项明细")

    # 查订单详情
    if order_id:
        resp = api("GET", f"/api/order/{order_id}", token=user_token)
        data = assert_ok(resp, f"查看订单详情 id={order_id}")
        if data:
            ok(f"  订单号: {data.get('orderNo')}")

    # 取消订单
    if order_id:
        log("取消最后一单")
        resp = api("PUT", f"/api/order/{order_id}/cancel", token=user_token)
        assert_ok(resp, f"取消订单 id={order_id}")

    return order_id


def test_admin_order(admin_token, order_id):
    heading("6. 订单管理 (管理员)")

    if admin_token is None:
        bad("缺少管理员 token，跳过")
        return

    # 查全部订单
    resp = api("GET", "/api/admin/order/page?page=1&size=10", token=admin_token)
    data = assert_ok(resp, "管理员查看全部订单")
    if data:
        ok(f"共 {data['total']} 个订单")

    # 改状态
    if data and data.get("records"):
        oid = data["records"][0]["id"]
        old_status = data["records"][0]["status"]
        new_status = 3 if old_status != 3 else 2
        log(f"修改订单状态 {oid}: {old_status} → {new_status}")
        resp = api("PUT", f"/api/admin/order/{oid}/status", token=admin_token, json={
            "status": new_status
        })
        assert_ok(resp, "修改订单状态")


def test_admin_user(admin_token):
    heading("7. 用户管理 (管理员)")

    if admin_token is None:
        bad("缺少管理员 token，跳过")
        return

    # 用户列表
    resp = api("GET", "/api/admin/user/page?page=1&size=10", token=admin_token)
    data = assert_ok(resp, "查看用户列表")
    if data:
        ok(f"共 {data['total']} 个用户")

    # 禁用/启用
    if data and data.get("records"):
        uid = data["records"][0]["id"]
        cur = data["records"][0]["status"]
        new = 0 if cur == 1 else 1
        log(f"切换用户 {uid} 状态: {cur} → {new}")
        resp = api("PUT", "/api/admin/user/status", token=admin_token, json={
            "id": uid, "status": new
        })
        assert_ok(resp, "修改用户状态")
        # 恢复
        resp = api("PUT", "/api/admin/user/status", token=admin_token, json={
            "id": uid, "status": cur
        })
        assert_ok(resp, "恢复用户状态")


def test_user_info(user_token):
    heading("8. 用户信息")

    if user_token is None:
        bad("缺少 token，跳过")
        return

    # 获取个人信息
    resp = api("GET", "/api/user/info", token=user_token)
    data = assert_ok(resp, "获取个人信息")
    if data:
        ok(f"用户名: {data.get('username')}  角色: {data.get('role')}")

    # 修改个人信息
    log("修改个人信息")
    resp = api("PUT", "/api/user/info", token=user_token, json={
        "realName": "测试用户", "phone": "13800138000"
    })
    assert_ok(resp, "修改个人信息")

    # 验证修改
    resp = api("GET", "/api/user/info", token=user_token)
    data = assert_ok(resp, "验证个人信息修改")
    if data:
        ok(f"真实姓名: {data.get('realName')}  手机: {data.get('phone')}")


def test_delete_cleanup(admin_token, dish_ids):
    heading("9. 清理测试数据")

    if admin_token is None:
        return

    # 删除菜品
    if dish_ids:
        for did in dish_ids:
            log(f"删除菜品 id={did}")
            resp = api("DELETE", f"/api/admin/dish/{did}", token=admin_token)
            assert_ok(resp, f"删除菜品 {did}")

    # 删除分类
    resp = api("GET", "/api/category/list")
    data = assert_ok(resp, "获取分类列表")
    if data:
        for cat in data:
            log(f"删除分类 id={cat['id']} ({cat['name']})")
            resp = api("DELETE", f"/api/admin/category/{cat['id']}", token=admin_token)
            assert_ok(resp, f"删除分类 {cat['name']}")


def test_analysis_apis(user_token, admin_token):
    heading("10. 数据分析接口 (需要数据库有分析数据)")

    tokens = {"user": user_token, "admin": admin_token}
    endpoints = [
        ("customer-flow", "客流分析"),
        ("peak-hour", "高峰时段分析"),
        ("dish-sales", "菜品销量"),
        ("prediction", "备餐预测"),
    ]

    for ep, label in endpoints:
        log(f"查询 {label} (普通用户)")
        resp = api("GET", f"/api/analysis/{ep}?page=1&size=5", token=user_token)
        data = assert_ok(resp, f"用户查看{label}")
        if data:
            ok(f"  {label}: 共 {data.get('total', 0)} 条记录")

        log(f"查询 {label} (管理员)")
        resp = api("GET", f"/api/analysis/{ep}?page=1&size=5", token=admin_token)
        data = assert_ok(resp, f"管理员查看{label}")
        if data:
            ok(f"  {label}: 共 {data.get('total', 0)} 条记录")

    log("未登录访问分析接口应被拦截")
    resp = api("GET", "/api/analysis/customer-flow")
    if resp.status_code == 401 or (resp.status_code == 200 and resp.json().get("code") == 401):
        ok("未登录被拒绝")
    else:
        bad("未登录应返回401", resp)


def main():
    global PASS, FAIL

    print("=" * 60)
    print("  Smart Canteen API 全接口测试")
    print(f"  目标服务: {BASE}")
    print("=" * 60)

    # 检查服务
    try:
        requests.get(f"{BASE}/api/category/list", timeout=3)
    except requests.ConnectionError:
        print("\n  [ERROR] 无法连接后端，请先启动 SpringBoot")
        sys.exit(1)

    # ---- 执行测试 ----
    user_token = test_user_flow()
    admin_token = test_admin_flow()

    cat_id, _ = test_category_crud(admin_token)
    dish_id, dish_ids = test_dish_crud(admin_token, cat_id)
    order_id = test_order_flow(user_token, dish_id)
    test_admin_order(admin_token, order_id)
    test_admin_user(admin_token)
    test_user_info(user_token)
    test_analysis_apis(user_token, admin_token)
    test_delete_cleanup(admin_token, dish_ids)

    # ---- 结果 ----
    print(f"\n{'='*60}")
    total = PASS + FAIL
    print(f"  总计: {total} 项测试 | 通过: {PASS} | 失败: {FAIL}")
    if FAIL == 0:
        print("  全部通过!")
        print(f"{'='*60}\n")
        sys.exit(0)
    else:
        print(f"  有 {FAIL} 项失败")
        print(f"{'='*60}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
