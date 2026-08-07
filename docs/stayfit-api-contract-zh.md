# Stay Fit API 中文说明

这份说明对应当前已经实现的接口：

```text
GET /api/stayfit/routine/
GET /api/stayfit/reshuffle/?current=step_jack
```

## 一句话理解

前端不要直接调用 wger。前端只调用我们自己的 HealthAge API。

```text
wger 原始动作资料
  -> 我们挑选和清洗
  -> Neon exercise 表，或本地 fallback pool
  -> HealthAge API 返回固定 JSON
  -> Stay Fit 页面渲染列表、Timer、Tips、弹窗
```

## routine API 返回什么

`GET /api/stayfit/routine/` 返回一个完整训练计划：

```json
{
  "plan_id": "mr_lim_cardio_core_beginner",
  "persona": {
    "name": "Mr Lim Wei Jian",
    "age": 48,
    "occupation": "Operations Manager",
    "location": "Urban Malaysia",
    "habits": [
      "rarely exercises",
      "eats irregularly",
      "sleeps late",
      "no recent screening"
    ]
  },
  "title": "Today's routine: cardio and core",
  "subtitle": "A short low-impact routine to build activity gradually.",
  "level": "beginner",
  "duration_minutes": 6,
  "exercises": [
    {
      "id": "step_jack",
      "wger_id": 1962,
      "name": "Step Jack",
      "category": "Cardio",
      "equipment": "none (bodyweight exercise)",
      "muscles": ["Quads", "Abs", "Glutes", "Shoulders"],
      "sets": 3,
      "reps": 15,
      "duration_seconds": null,
      "instructions": "Stand upright with your feet together...",
      "image_url": "https://wger.de/media/exercise-images/1962/...",
      "video_url": null,
      "source_url": "https://wger.de/api/v2/exerciseinfo/1962/"
    }
  ],
  "guidance_tip": {
    "title": "Tip",
    "text": "Move at your own pace and take breaks when you need to."
  },
  "safety_note": "Start gently. Stop if you feel chest pain, dizziness, unusual shortness of breath, or sharp pain.",
  "guideline_note": "Exercise recommendations align with Saranan Aktiviti Fizikal Malaysia and support SDG3 Good Health and Well-Being."
}
```

## 字段中文解释

| 字段 | 中文意思 | 谁负责 |
| --- | --- | --- |
| `plan_id` | 这个训练计划的 ID | 我们自己定义 |
| `persona` | Mr. Lim 的人物画像信息 | 我们自己定义 |
| `title` | 页面标题 | 我们自己定义 |
| `subtitle` | 页面副标题 | 我们自己定义 |
| `level` | 难度等级，例如 beginner | 我们自己定义 |
| `duration_minutes` | 默认总训练时长 | 我们自己定义 |
| `exercises` | 四个动作列表 | wger 数据加我们筛选 |
| `wger_id` | wger 原始动作 ID | 来自 wger |
| `name` | 动作名称 | 来自 wger，必要时我们改成更适合 demo 的名字 |
| `category` | 动作分类，比如 Cardio、Abs | 来自 wger |
| `equipment` | 需要的器械 | 来自 wger |
| `muscles` | 训练到的肌肉 | 来自 wger |
| `sets` | 做几组 | 我们自己定义 |
| `reps` | 每组做几次 | 我们自己定义 |
| `duration_seconds` | 每组持续多少秒 | 我们自己定义 |
| `instructions` | 动作说明 | wger 原文基础上清洗和简化 |
| `image_url` | 动作图片 | 来自 wger，有就显示 |
| `video_url` | 动作视频 | 来自 wger，有就显示 |
| `guidance_tip` | 右边 Tips 区域 | 我们自己定义 |
| `safety_note` | 安全提醒 | 我们自己定义 |
| `guideline_note` | 马来西亚运动指南说明 | 我们自己定义 |

## Tips 区域从哪里来

Tips 不应该直接调用 wger。

wger 负责的是动作资料，比如动作名称、图片、视频、说明。右侧 Tips 是 HealthAge 自己的安全和行为提醒，应该来自：

```text
用户故事 3.8.3 Guidance Panel
用户故事 3.3.4 Guideline Alignment Disclaimer
```

所以 Tips 应该写成：

```text
Move at your own pace and take breaks when you need to.
```

而不是从 wger 某个字段硬抓。

## wger 能提供什么

wger 的 `exerciseinfo` 数据可以提供：

```text
id / uuid
category
muscles
equipment
images
videos
translations.name
translations.description
translations.aliases
license
license_author
```

wger 不能替我们决定：

```text
Mr. Lim 应该做哪四个动作
每个动作做几组几次
这个 routine 的标题
右边 Tips 写什么
是否适合 demo
是否适合中年低强度入门场景
```

这些都属于 HealthAge 的 MVP 产品逻辑。

## Neon 和 fallback 的关系

当前代码已经实现：

```text
如果 Neon/Postgres 中存在 exercise 表
  -> /api/stayfit/routine/ 优先读取 Neon
如果 exercise 表不存在、字段不匹配或数据库不可用
  -> 自动使用 core/stayfit_api.py 里的本地 fallback 数据
```

所以明天前端同学可以放心继续做页面；即使 Neon 还没 seed，页面也能正常 demo。

Neon 建表和 seed 文件在：

```text
docs/sql/stayfit_exercise_seed.sql
```

## reshuffle API 返回什么

`GET /api/stayfit/reshuffle/?current=step_jack` 返回一个替换动作：

```json
{
  "exercise": {
    "id": "deep_breathing",
    "wger_id": 1591,
    "name": "Deep Breathing",
    "category": "Chest",
    "sets": 2,
    "duration_seconds": 45
  }
}
```

前端收到后，只替换当前那一行，其他三个动作不变。
