from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# 创建FastAPI应用实例
app = FastAPI(
    title="演示API",
    description="一个简单的FastAPI演示",
    version="1.0.0"
)


# 数据模型定义
class User(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None
    created_at: datetime = datetime.now()


class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None


# 模拟数据库
fake_users_db = []
current_id = 1


# 根路径
@app.get("/")
async def root():
    return {
        "message": "欢迎使用FastAPI演示",
        "timestamp": datetime.now(),
        "endpoints": [
            "/docs - API文档",
            "/users - 获取所有用户",
            "/users/{id} - 获取特定用户"
        ]
    }


# 获取所有用户
@app.get("/users", response_model=List[User])
async def get_users(
        skip: int = Query(0, description="跳过前N个用户"),
        limit: int = Query(10, description="限制返回数量")
):
    return fake_users_db[skip:skip + limit]


# 根据ID获取用户
@app.get("/users/{user_id}", response_model=User)
async def get_user(
        user_id: int = Path(..., description="用户ID", gt=0)
):
    user = next((u for u in fake_users_db if u.id == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


# 创建新用户
@app.post("/users", response_model=User)
async def create_user(user: UserCreate):
    global current_id
    new_user = User(
        id=current_id,
        name=user.name,
        email=user.email,
        age=user.age
    )
    fake_users_db.append(new_user)
    current_id += 1
    return new_user


# 更新用户信息
@app.put("/users/{user_id}", response_model=User)
async def update_user(
        user_id: int,
        user_update: UserUpdate
):
    user_index = next((i for i, u in enumerate(fake_users_db) if u.id == user_id), None)

    if user_index is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    existing_user = fake_users_db[user_index]

    # 只更新提供的字段
    update_data = user_update.dict(exclude_unset=True)
    updated_user = existing_user.copy(update=update_data)
    fake_users_db[user_index] = updated_user

    return updated_user


# 删除用户
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    user_index = next((i for i, u in enumerate(fake_users_db) if u.id == user_id), None)

    if user_index is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    deleted_user = fake_users_db.pop(user_index)

    return {
        "message": "用户删除成功",
        "deleted_user": deleted_user
    }


# 搜索用户
@app.get("/users/search/")
async def search_users(
        name: Optional[str] = Query(None, description="按姓名搜索"),
        email: Optional[str] = Query(None, description="按邮箱搜索")
):
    results = fake_users_db

    if name:
        results = [u for u in results if name.lower() in u.name.lower()]

    if email:
        results = [u for u in results if email.lower() in u.email.lower()]

    return results


# 健康检查端点
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "total_users": len(fake_users_db)
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)