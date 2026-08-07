# Stay Fit 明日交接说明

## 当前完成状态

Stay Fit 已经有一版可运行 MVP：

- 页面：`/stayfit/`
- routine API：`/api/stayfit/routine/?risk=heart_disease`
- reshuffle API：`/api/stayfit/reshuffle/?current=step_jack&risk=heart_disease`
- 前端 JS：`core/static/core/js/stayfit.js`
- 后端数据/API：`core/stayfit_api.py`
- 中文 API 说明：`docs/stayfit-api-contract-zh.md`
- Neon seed SQL：`docs/sql/stayfit_exercise_seed.sql`

当前页面已经支持：

- 在 Stay Fit 页面选择疾病/风险 focus：Heart disease、Stroke、Type 2 diabetes、Respiratory disease、Cancer
- 根据选中的 focus 调用不同 routine；选择只作为 query 参数传递，不保存到数据库或 session
- 从 API 动态加载四个 exercise
- 点击 exercise 打开 detail modal
- modal 显示 instructions / equipment / muscles / image fallback
- 点击 Swap 替换单个 exercise
- Timer 支持 Start / Pause / Reset / +1 min / complete state
- 右侧 Tips 和 safety note

## 如何运行

在 `HealthAge` 目录执行：

```powershell
..\tmp\healthage-venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --noreload
```

打开：

```text
http://127.0.0.1:8000/stayfit/
http://127.0.0.1:8000/api/stayfit/routine/
http://127.0.0.1:8000/api/stayfit/routine/?risk=respiratory_disease
```

运行测试：

```powershell
..\tmp\healthage-venv\Scripts\python.exe manage.py test --noinput
```

## 给前端同学的边界

前端同学主要改这三个文件：

```text
core/templates/core/stayfit.html
core/static/core/js/stayfit.js
core/static/core/css/style.css
```

她可以继续做：

- UI polish，让页面更贴近 Figma/截图
- Health focus 按钮的视觉细节和移动端排版
- Timer 圆环视觉细化
- Modal 动画和排版优化
- 图片缺失时的 fallback 视觉
- Loading / error state polish
- 移动端布局检查

她不需要碰：

```text
core/stayfit_api.py
core/views.py
healthrisk/urls.py
docs/sql/stayfit_exercise_seed.sql
Neon
wger raw API
```

## 给后端同学/你的边界

你继续负责：

- API contract 稳定
- disease/risk 到 exercise routine 的映射是否合理
- exercise 数据正确
- Neon seed 和 fallback
- 测试
- README / LeanKit 说明

当前 `core/stayfit_api.py` 的逻辑是：

```text
如果 Neon/Postgres 中存在 exercise 表
  -> 从 exercise 表读取
否则
  -> 使用 Python fallback exercise pool
```

所以 demo 不会因为 Neon 没准备好而坏掉。

现在 disease/risk 选择的职责分工是：

```text
Stay Fit 页面按钮
  -> /api/stayfit/routine/?risk=<risk_key>
  -> core/stayfit_api.py 选择四个动作
  -> 前端渲染 routine
```

`risk_key` 当前支持：

```text
heart_disease
stroke
type_2_diabetes
respiratory_disease
cancer
```

这个选择不保存用户数据，只影响当前页面展示。

## Neon 下一步

如要正式让 API 从 Neon 读 exercise：

1. 打开 Neon SQL Editor。
2. 先确认没有会被覆盖的生产 `exercise` 表。
3. 执行：

```text
docs/sql/stayfit_exercise_seed.sql
```

4. 刷新：

```text
http://127.0.0.1:8000/api/stayfit/routine/
```

如果 `exercise` 表存在且字段匹配，API 会自动优先读 Neon。

## 还没做的功能

先不要混进当前 MVP，除非基础功能已经很稳：

- 7-day check-in modal
- `/api/stayfit/review/`
- 根据 review 结果返回 reduce / maintain / progress
- 保存用户 workout history
- 真实登录用户数据

这些属于下一阶段，不是当前 Stay Fit 页面最小闭环。

## 明天建议验收清单

- 页面打开后四个动作能显示
- Health focus 按钮能切换不同 disease/risk routine
- 切换 focus 后 URL 只出现 `risk=` query，不写 session 或数据库
- API 返回 JSON，且 exercises 长度为 4
- 点击每个动作都能打开 modal
- 有图片的动作显示图片，没图片的动作显示文字 fallback
- Swap 只替换当前那一行
- Timer 可以 Start / Pause / Reset
- 倒计时到 00:00 后显示完成状态
- Tips 和 safety note 不溢出
- 页面在笔记本宽度下不重叠
- `manage.py test --noinput` 通过
