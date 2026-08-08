"""Stay Fit routine data contract for the MVP.

This module deliberately returns small curated routines instead of proxying
wger live during the user flow. The exercise facts are wger-sourced where
available; the condition-to-routine mapping, sets, reps, duration and tips are
HealthAge MVP logic.
"""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any

from django.conf import settings
from django.db import DatabaseError, connection


MR_LIM_PERSONA = {
    "name": "Mr Lim Wei Jian",
    "age": 48,
    "occupation": "Operations Manager",
    "location": "Urban Malaysia",
    "habits": [
        "rarely exercises",
        "eats irregularly",
        "sleeps late",
        "no recent screening",
    ],
    "goal": "Build healthier habits gradually without feeling overwhelmed.",
}


EXERCISE_POOL = [
    {
        "id": "step_jack",
        "wger_id": 1962,
        "wger_uuid": "2f10d91f-6c12-471b-bb9e-80840a56ce01",
        "name": "Step Jack",
        "category": "Cardio",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Quads", "Abs", "Glutes", "Shoulders"],
        "sets": 3,
        "reps": 15,
        "duration_seconds": None,
        "instructions": (
            "Stand upright with your feet together. Step one foot to the side "
            "while raising both arms, return to the centre, then alternate sides "
            "at a steady pace."
        ),
        "image_url": "https://wger.de/media/exercise-images/1962/74041371-1019-4f89-9ebe-cec792484a46.png",
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1962/",
        "source_note": "Exercise name, category, muscles, equipment and image are sourced from wger.",
        "difficulty": "beginner",
        "plan_tags": ["cardio_core", "mobility", "heart_disease", "stroke", "type_2_diabetes", "respiratory_disease"],
    },
    {
        "id": "bird_dog",
        "wger_id": 1572,
        "wger_uuid": None,
        "name": "Bird Dog",
        "category": "Abs",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Abs", "Glutes", "Shoulders"],
        "sets": 3,
        "reps": 10,
        "duration_seconds": None,
        "instructions": (
            "Begin on all fours with hands under shoulders and knees under hips. "
            "Extend one arm and the opposite leg, pause briefly, then return and "
            "switch sides."
        ),
        "image_url": "https://wger.de/media/exercise-images/1572/3d14e761-a73d-49da-8804-f3016a7573ff.png",
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1572/",
        "source_note": "Exercise name, category, equipment, image and base instructions are sourced from wger.",
        "difficulty": "beginner",
        "plan_tags": [
            "cardio_core",
            "strength",
            "heart_disease",
            "stroke",
            "type_2_diabetes",
            "respiratory_disease",
            "cancer",
        ],
    },
    {
        "id": "wall_push_up",
        "wger_id": 1551,
        "wger_uuid": None,
        "name": "Wall Push-up",
        "category": "Chest",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Chest", "Shoulders", "Triceps"],
        "sets": 3,
        "reps": 12,
        "duration_seconds": None,
        "instructions": (
            "Stand facing a wall with hands at chest height. Bend your elbows "
            "gently to bring your body closer to the wall, then push back to the "
            "start position."
        ),
        "image_url": "https://wger.de/media/exercise-images/1551/a6a9e561-3965-45c6-9f2b-ee671e1a3a45.png",
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1551/",
        "source_note": "Adapted as a low-impact variation of the wger Push-Up entry for the MVP routine.",
        "difficulty": "beginner",
        "plan_tags": ["cardio_core", "strength", "heart_disease", "type_2_diabetes"],
    },
    {
        "id": "side_plank_knee",
        "wger_id": 580,
        "wger_uuid": None,
        "name": "Side Plank from Knees",
        "category": "Abs",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Abs", "Obliques"],
        "sets": 3,
        "reps": None,
        "duration_seconds": 20,
        "instructions": (
            "Lie on your side and support your body with your forearm and knees. "
            "Keep your hips lifted and hold a steady, comfortable position."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/580/",
        "source_note": "Adapted from the wger Side Plank entry with a beginner knee-supported variation.",
        "difficulty": "beginner",
        "plan_tags": ["cardio_core", "strength", "heart_disease", "stroke", "cancer"],
    },
    {
        "id": "deep_breathing",
        "wger_id": 1591,
        "wger_uuid": None,
        "name": "Deep Breathing",
        "category": "Chest",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Chest"],
        "sets": 2,
        "reps": None,
        "duration_seconds": 45,
        "instructions": (
            "Sit or stand tall. Breathe in slowly through your nose, let your "
            "chest and belly expand, then breathe out steadily."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1591/",
        "source_note": "Exercise name and base concept are sourced from wger.",
        "difficulty": "beginner",
        "plan_tags": ["mobility", "cardio_core", "heart_disease", "respiratory_disease", "cancer"],
    },
    {
        "id": "torso_rotation",
        "wger_id": 1451,
        "wger_uuid": None,
        "name": "Torso Rotation Stretch",
        "category": "Chest",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Abs", "Back"],
        "sets": 2,
        "reps": 8,
        "duration_seconds": None,
        "instructions": (
            "Stand or sit upright. Rotate your torso slowly to one side, hold "
            "briefly, then return to centre and repeat on the other side."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1451/",
        "source_note": "Exercise name and base instructions are sourced from wger.",
        "difficulty": "beginner",
        "plan_tags": ["mobility", "cardio_core", "stroke", "type_2_diabetes", "respiratory_disease", "cancer"],
    },
    {
        "id": "seated_march",
        "wger_id": None,
        "wger_uuid": None,
        "name": "Seated March",
        "category": "Cardio",
        "equipment": "chair",
        "muscles": ["Quads", "Hip flexors", "Abs"],
        "sets": 2,
        "reps": 20,
        "duration_seconds": None,
        "instructions": (
            "Sit tall near the front of a chair. Lift one knee at a time as if "
            "marching, keeping the movement slow and controlled."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://infosihat.moh.gov.my/multimedia/garis-panduan/item/garis-panduan-aktiviti-fizikal-malaysia-2.html",
        "source_note": "HealthAge curated beginner movement aligned with the Malaysian physical activity guideline.",
        "difficulty": "beginner",
        "plan_tags": ["cardio_core", "mobility", "heart_disease", "stroke", "type_2_diabetes", "respiratory_disease", "cancer"],
    },
    {
        "id": "chair_squat",
        "wger_id": None,
        "wger_uuid": None,
        "name": "Chair Squat",
        "category": "Legs",
        "equipment": "chair",
        "muscles": ["Quads", "Glutes", "Hamstrings"],
        "sets": 2,
        "reps": 10,
        "duration_seconds": None,
        "instructions": (
            "Stand in front of a chair with feet hip-width apart. Sit back until "
            "you lightly touch the chair, then stand up again without rushing."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://infosihat.moh.gov.my/multimedia/garis-panduan/item/garis-panduan-aktiviti-fizikal-malaysia-2.html",
        "source_note": "HealthAge curated beginner movement aligned with the Malaysian physical activity guideline.",
        "difficulty": "beginner",
        "plan_tags": ["strength", "cardio_core", "heart_disease", "type_2_diabetes", "cancer"],
    },
    {
        "id": "heel_raise",
        "wger_id": None,
        "wger_uuid": None,
        "name": "Standing Heel Raise",
        "category": "Calves",
        "equipment": "chair or wall support",
        "muscles": ["Calves", "Ankles"],
        "sets": 2,
        "reps": 12,
        "duration_seconds": None,
        "instructions": (
            "Stand tall with a chair or wall nearby for support. Rise onto the "
            "balls of your feet, pause briefly, then lower your heels slowly."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://infosihat.moh.gov.my/multimedia/garis-panduan/item/garis-panduan-aktiviti-fizikal-malaysia-2.html",
        "source_note": "HealthAge curated beginner movement aligned with the Malaysian physical activity guideline.",
        "difficulty": "beginner",
        "plan_tags": ["mobility", "strength", "heart_disease", "stroke", "type_2_diabetes"],
    },
    {
        "id": "shoulder_roll",
        "wger_id": None,
        "wger_uuid": None,
        "name": "Shoulder Roll",
        "category": "Shoulders",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Shoulders", "Upper back"],
        "sets": 2,
        "reps": 10,
        "duration_seconds": None,
        "instructions": (
            "Sit or stand tall. Roll both shoulders slowly up, back and down, "
            "then repeat in the opposite direction."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://infosihat.moh.gov.my/multimedia/garis-panduan/item/garis-panduan-aktiviti-fizikal-malaysia-2.html",
        "source_note": "HealthAge curated beginner movement aligned with the Malaysian physical activity guideline.",
        "difficulty": "beginner",
        "plan_tags": ["mobility", "stroke", "respiratory_disease", "cancer"],
    },
    {
        "id": "knee_extension",
        "wger_id": None,
        "wger_uuid": None,
        "name": "Seated Knee Extension",
        "category": "Legs",
        "equipment": "chair",
        "muscles": ["Quads"],
        "sets": 2,
        "reps": 10,
        "duration_seconds": None,
        "instructions": (
            "Sit tall with both feet on the floor. Straighten one knee until the "
            "lower leg is nearly level, pause, then lower and switch sides."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://infosihat.moh.gov.my/multimedia/garis-panduan/item/garis-panduan-aktiviti-fizikal-malaysia-2.html",
        "source_note": "HealthAge curated beginner movement aligned with the Malaysian physical activity guideline.",
        "difficulty": "beginner",
        "plan_tags": ["strength", "mobility", "stroke", "type_2_diabetes", "cancer"],
    },
    {
        "id": "side_step",
        "wger_id": None,
        "wger_uuid": None,
        "name": "Standing Side Step",
        "category": "Cardio",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Glutes", "Quads", "Hips"],
        "sets": 2,
        "reps": 12,
        "duration_seconds": None,
        "instructions": (
            "Stand tall and step one foot to the side, then bring the other foot "
            "in. Repeat side to side at a comfortable pace."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://infosihat.moh.gov.my/multimedia/garis-panduan/item/garis-panduan-aktiviti-fizikal-malaysia-2.html",
        "source_note": "HealthAge curated beginner movement aligned with the Malaysian physical activity guideline.",
        "difficulty": "beginner",
        "plan_tags": ["cardio_core", "mobility", "heart_disease", "stroke", "type_2_diabetes", "respiratory_disease"],
    },
    {
        "id": "walking",
        "wger_id": 1104,
        "wger_uuid": None,
        "name": "Walking",
        "category": "Cardio",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Hamstrings", "Calves", "Glutes", "Quads", "Abs"],
        "sets": 1,
        "reps": None,
        "duration_seconds": 60,
        "instructions": (
            "Walk indoors or outdoors at a comfortable pace. Keep your posture "
            "tall, swing your arms naturally, and slow down before you feel out "
            "of breath."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1104/",
        "source_note": "Exercise name, category, muscles and equipment are sourced from wger; instructions are adapted for the HealthAge MVP.",
        "difficulty": "beginner",
        "plan_tags": ["cardio_core", "mobility", "heart_disease", "stroke", "type_2_diabetes", "respiratory_disease", "cancer"],
    },
    {
        "id": "marching_high_knees",
        "wger_id": 1965,
        "wger_uuid": None,
        "name": "Marching High Knees",
        "category": "Legs",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Quads", "Calves", "Glutes", "Abs"],
        "sets": 2,
        "reps": 12,
        "duration_seconds": None,
        "instructions": (
            "Stand tall and lift one knee toward your chest as high as comfortable. "
            "Lower it with control, then switch sides. Use a wall or chair if "
            "balance feels uncertain."
        ),
        "image_url": "https://wger.de/media/exercise-images/1965/03c08a42-dedb-4a46-8d15-acaf497a35a2.png",
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1965/",
        "source_note": "Exercise name, category, muscles, equipment and image are sourced from wger; instructions are adapted for the HealthAge MVP.",
        "difficulty": "beginner",
        "plan_tags": ["cardio_core", "mobility", "heart_disease", "stroke", "type_2_diabetes", "respiratory_disease", "cancer"],
    },
    {
        "id": "diaphragmatic_breathing",
        "wger_id": 1940,
        "wger_uuid": None,
        "name": "Diaphragmatic Breathing",
        "category": "Cardio",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Chest", "Abs"],
        "sets": 2,
        "reps": None,
        "duration_seconds": 45,
        "instructions": (
            "Sit or lie comfortably. Place one hand on your chest and one on your "
            "belly. Breathe in so the belly hand rises, then breathe out slowly."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1940/",
        "source_note": "Exercise name, category and equipment are sourced from wger; instructions are adapted for the HealthAge MVP.",
        "difficulty": "beginner",
        "plan_tags": ["mobility", "cardio_core", "heart_disease", "stroke", "respiratory_disease", "cancer"],
    },
    {
        "id": "arm_neck_stretch",
        "wger_id": 1590,
        "wger_uuid": None,
        "name": "Arm and Neck Stretch",
        "category": "Abs",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Shoulders", "Trapezius", "Triceps", "Lats"],
        "sets": 2,
        "reps": None,
        "duration_seconds": 30,
        "instructions": (
            "Sit or stand tall. Gently reach one arm across the body and relax "
            "the neck on the opposite side. Hold without pulling sharply, then "
            "switch sides."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1590/",
        "source_note": "Exercise name, category, muscles and equipment are sourced from wger; instructions are adapted for the HealthAge MVP.",
        "difficulty": "beginner",
        "plan_tags": ["mobility", "heart_disease", "stroke", "respiratory_disease", "cancer"],
    },
    {
        "id": "back_neck_stretch",
        "wger_id": 1010,
        "wger_uuid": None,
        "name": "Back Neck Stretch",
        "category": "Back",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Neck", "Upper back"],
        "sets": 2,
        "reps": None,
        "duration_seconds": 25,
        "instructions": (
            "Sit upright and slowly lower your chin toward your chest. Keep the "
            "stretch light, breathe steadily, then return to neutral."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1010/",
        "source_note": "Exercise name, category and equipment are sourced from wger; instructions are adapted for the HealthAge MVP.",
        "difficulty": "beginner",
        "plan_tags": ["mobility", "stroke", "respiratory_disease", "cancer"],
    },
    {
        "id": "forward_shoulder_rotation",
        "wger_id": 1004,
        "wger_uuid": None,
        "name": "Forward Shoulder Rotation",
        "category": "Back",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Shoulders", "Upper back"],
        "sets": 2,
        "reps": 10,
        "duration_seconds": None,
        "instructions": (
            "Place your fingertips lightly on your shoulders. Circle both elbows "
            "forward in a smooth motion, keeping the neck relaxed."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1004/",
        "source_note": "Exercise name, category and equipment are sourced from wger; instructions are adapted for the HealthAge MVP.",
        "difficulty": "beginner",
        "plan_tags": ["mobility", "heart_disease", "stroke", "respiratory_disease", "cancer"],
    },
    {
        "id": "standing_calf_stretch",
        "wger_id": 1239,
        "wger_uuid": None,
        "name": "Standing Calf Stretch",
        "category": "Legs",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Calves"],
        "sets": 2,
        "reps": None,
        "duration_seconds": 25,
        "instructions": (
            "Stand facing a wall. Step one foot back, keep the back heel down, "
            "and lean forward gently until the calf feels stretched. Switch sides."
        ),
        "image_url": "https://wger.de/media/exercise-images/1239/5026373a-a7b4-4e26-a0aa-c46634205196.jpg",
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1239/",
        "source_note": "Exercise name, category, muscles, equipment and image are sourced from wger; instructions are adapted for the HealthAge MVP.",
        "difficulty": "beginner",
        "plan_tags": ["mobility", "heart_disease", "stroke", "type_2_diabetes", "cancer"],
    },
    {
        "id": "knee_to_chest_stretch",
        "wger_id": 1452,
        "wger_uuid": None,
        "name": "Knee to Chest Stretch",
        "category": "Legs",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Glutes", "Hamstrings"],
        "sets": 2,
        "reps": None,
        "duration_seconds": 25,
        "instructions": (
            "Lie on your back or sit tall. Bring one knee gently toward the chest, "
            "hold without forcing, then release and switch sides."
        ),
        "image_url": "https://wger.de/media/exercise-images/1452/85a6b9de-4eec-445b-8ebb-f1950b076aba.png",
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1452/",
        "source_note": "Exercise name, category, muscles, equipment and image are sourced from wger; instructions are adapted for the HealthAge MVP.",
        "difficulty": "beginner",
        "plan_tags": ["mobility", "stroke", "type_2_diabetes", "cancer"],
    },
    {
        "id": "wall_angels",
        "wger_id": 1679,
        "wger_uuid": None,
        "name": "Wall Angels",
        "category": "Shoulders",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Trapezius", "Shoulders"],
        "sets": 2,
        "reps": 8,
        "duration_seconds": None,
        "instructions": (
            "Stand with your back near a wall. Slide your arms upward and downward "
            "like making a snow angel, keeping the movement slow and pain-free."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1679/",
        "source_note": "Exercise name, category and muscles are sourced from wger; instructions are adapted for the HealthAge MVP.",
        "difficulty": "beginner",
        "plan_tags": ["mobility", "stroke", "respiratory_disease", "cancer"],
    },
    {
        "id": "wall_slides",
        "wger_id": 716,
        "wger_uuid": None,
        "name": "Wall Slides",
        "category": "Back",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Chest", "Trapezius", "Triceps", "Hamstrings"],
        "sets": 2,
        "reps": 8,
        "duration_seconds": None,
        "instructions": (
            "Stand with your back against a wall and elbows bent. Slide your arms "
            "up the wall as far as comfortable, then lower them with control."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/716/",
        "source_note": "Exercise name, category, muscles and equipment are sourced from wger; instructions are adapted for the HealthAge MVP.",
        "difficulty": "beginner",
        "plan_tags": ["mobility", "heart_disease", "stroke", "respiratory_disease", "cancer"],
    },
    {
        "id": "hip_raise_lying",
        "wger_id": 292,
        "wger_uuid": None,
        "name": "Hip Raise, Lying",
        "category": "Back",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Glutes", "Hamstrings"],
        "sets": 2,
        "reps": 10,
        "duration_seconds": None,
        "instructions": (
            "Lie on your back with knees bent and feet flat. Lift your hips slowly, "
            "pause briefly, then lower with control."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/292/",
        "source_note": "Exercise name, category, muscles and equipment are sourced from wger; instructions are adapted for the HealthAge MVP.",
        "difficulty": "beginner",
        "plan_tags": ["strength", "mobility", "heart_disease", "stroke", "type_2_diabetes", "cancer"],
    },
    {
        "id": "good_morning",
        "wger_id": 1392,
        "wger_uuid": None,
        "name": "Good Morning",
        "category": "Legs",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Hamstrings", "Glutes", "Back"],
        "sets": 2,
        "reps": 8,
        "duration_seconds": None,
        "instructions": (
            "Stand with feet hip-width apart and hands on hips. Hinge forward "
            "slightly from the hips with a flat back, then return to standing."
        ),
        "image_url": "https://wger.de/media/exercise-images/1392/a02c9c7d-f42d-43e0-9946-1b99b014daee.png",
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1392/",
        "source_note": "Exercise name, category, muscles, equipment and image are sourced from wger; instructions are adapted for the HealthAge MVP.",
        "difficulty": "beginner",
        "plan_tags": ["strength", "mobility", "heart_disease", "type_2_diabetes", "cancer"],
    },
    {
        "id": "side_stretch",
        "wger_id": 1861,
        "wger_uuid": None,
        "name": "Side Stretch",
        "category": "Back",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Back", "Obliques"],
        "sets": 2,
        "reps": None,
        "duration_seconds": 25,
        "instructions": (
            "Stand or sit tall. Reach one arm overhead and lean gently to the "
            "opposite side. Keep breathing, then return and switch sides."
        ),
        "image_url": "https://wger.de/media/exercise-images/1861/0ffe4e99-71ad-47fb-b98c-1f243faa0499.png",
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1861/",
        "source_note": "Exercise name, category, equipment and image are sourced from wger; instructions are adapted for the HealthAge MVP.",
        "difficulty": "beginner",
        "plan_tags": ["mobility", "heart_disease", "stroke", "respiratory_disease", "cancer"],
    },
    {
        "id": "shoulder_shrug",
        "wger_id": 570,
        "wger_uuid": None,
        "name": "Shoulder Shrug",
        "category": "Shoulders",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Trapezius"],
        "sets": 2,
        "reps": 10,
        "duration_seconds": None,
        "instructions": (
            "Stand or sit tall with arms relaxed. Lift both shoulders toward your "
            "ears, pause briefly, then lower them slowly."
        ),
        "image_url": "https://wger.de/media/exercise-images/570/68b4a33f-40f1-4dda-b56c-a2e20ed13903.jpg",
        "video_url": "https://wger.de/media/exercise-video/570/bd1f14a3-9d2b-4ec0-b6b9-e82d739f7e60.MOV",
        "source_url": "https://wger.de/api/v2/exerciseinfo/570/",
        "source_note": "Exercise name, category, muscles, equipment, image and video are sourced from wger; instructions are adapted for the HealthAge MVP.",
        "difficulty": "beginner",
        "plan_tags": ["mobility", "heart_disease", "stroke", "respiratory_disease", "cancer"],
    },
]


DEFAULT_RISK_KEY = "heart_disease"

INTENSITY_LEVELS = {
    "beginner": {
        "label": "Low",
        "description": "Lower volume for first-time or cautious users.",
        "duration_delta": 0,
        "sets_delta": 0,
        "reps_delta": 0,
        "hold_delta": 0,
        "tip_prefix": "Low intensity: keep the movement easy and stop before fatigue builds.",
    },
    "standard": {
        "label": "Medium",
        "description": "A moderate version for users comfortable with light activity.",
        "duration_delta": 2,
        "sets_delta": 1,
        "reps_delta": 3,
        "hold_delta": 10,
        "tip_prefix": "Medium intensity: keep breathing steady and rest between sets.",
    },
    "progress": {
        "label": "High",
        "description": "More volume for users already comfortable with the routine.",
        "duration_delta": 4,
        "sets_delta": 1,
        "reps_delta": 5,
        "hold_delta": 15,
        "tip_prefix": "High intensity: use this only if the easier versions feel comfortable.",
    },
}

RISK_ROUTINES = {
    "heart_disease": {
        "label": "Heart disease",
        "description": "Low-impact cardio plus light strength.",
        "plan_tag": "heart_disease",
        "exercise_ids": ["step_jack", "chair_squat", "wall_push_up", "seated_march"],
        "title": "Heart disease: low-impact cardio and core",
        "subtitle": "A short routine to build activity gradually without high impact.",
        "duration_minutes": 6,
        "reason": (
            "This focus uses steady low-impact movement, light upper-body strength "
            "and simple core control to support gradual activity building."
        ),
        "tip": "Keep the pace conversational. Stop and seek help if chest pain or dizziness appears.",
    },
    "stroke": {
        "label": "Stroke",
        "description": "Controlled mobility, balance and core work.",
        "plan_tag": "stroke",
        "exercise_ids": ["torso_rotation", "seated_march", "heel_raise", "bird_dog"],
        "title": "Stroke: mobility and control",
        "subtitle": "A gentle routine focused on controlled movement and stability.",
        "duration_minutes": 6,
        "reason": (
            "This focus uses slow mobility and core-stability movements that are "
            "easy to control and can be paused between sets."
        ),
        "tip": "Move slowly and keep support nearby if balance feels uncertain.",
    },
    "type_2_diabetes": {
        "label": "Type 2 diabetes",
        "description": "Light cardio and strength to support activity habits.",
        "plan_tag": "type_2_diabetes",
        "exercise_ids": ["step_jack", "chair_squat", "knee_extension", "side_step"],
        "title": "Type 2 diabetes: cardio and strength starter",
        "subtitle": "A beginner routine that mixes movement, strength and mobility.",
        "duration_minutes": 7,
        "reason": (
            "This focus combines simple cardio with light strength work because "
            "regular activity is a practical first habit for metabolic health."
        ),
        "tip": "Start after a light warm-up and keep water nearby.",
    },
    "respiratory_disease": {
        "label": "Respiratory disease",
        "description": "Breathing-led mobility at an easy pace.",
        "plan_tag": "respiratory_disease",
        "exercise_ids": ["deep_breathing", "shoulder_roll", "torso_rotation", "seated_march"],
        "title": "Respiratory disease: breathing and mobility",
        "subtitle": "A gentle routine that starts with breathing and avoids high intensity.",
        "duration_minutes": 6,
        "reason": (
            "This focus starts with breathing control, then adds low-intensity "
            "mobility and short movement blocks."
        ),
        "tip": "Use a slower pace than usual and pause if breathing becomes uncomfortable.",
    },
    "cancer": {
        "label": "Cancer",
        "description": "Gentle mobility and core activation.",
        "plan_tag": "cancer",
        "exercise_ids": ["deep_breathing", "shoulder_roll", "knee_extension", "side_plank_knee"],
        "title": "Cancer: gentle mobility starter",
        "subtitle": "A low-pressure routine for general movement and body awareness.",
        "duration_minutes": 6,
        "reason": (
            "This focus keeps the routine gentle and avoids intense loading. It is "
            "only general activity support, not cancer treatment guidance."
        ),
        "tip": "Keep the effort light and check with a clinician if you are in active treatment.",
    },
}

RISK_ALIASES = {
    "heart": "heart_disease",
    "heart_disease": "heart_disease",
    "cardio": "heart_disease",
    "high_blood_pressure": "heart_disease",
    "stroke": "stroke",
    "diabetes": "type_2_diabetes",
    "type_2_diabetes": "type_2_diabetes",
    "type2_diabetes": "type_2_diabetes",
    "pneumonia": "respiratory_disease",
    "respiratory": "respiratory_disease",
    "respiratory_disease": "respiratory_disease",
    "chronic_lung_disease": "respiratory_disease",
    "tuberculosis": "respiratory_disease",
    "cancer": "cancer",
    "lung_cancer": "cancer",
    "bowel_cancer": "cancer",
    "breast_cancer": "cancer",
    "liver_cancer": "cancer",
    "cervical_cancer": "cancer",
    "ovarian_cancer": "cancer",
    "leukaemia": "cancer",
}

DEFAULT_ROUTINE_IDS = RISK_ROUTINES[DEFAULT_RISK_KEY]["exercise_ids"]


def build_stayfit_routine(level: str = "beginner", risk_key: str | None = None) -> dict[str, Any]:
    """Return the stable JSON contract consumed by the Stay Fit frontend."""
    selected_key = _normalise_risk_key(risk_key)
    selected_level = _normalise_level(level)
    routine_config = RISK_ROUTINES[selected_key]
    level_config = INTENSITY_LEVELS[selected_level]
    exercise_pool = _load_exercise_pool()
    exercises = [
        _scale_exercise_for_level(exercise, level_config)
        for exercise in _select_exercises(exercise_pool, routine_config["exercise_ids"])
    ]
    duration_minutes = routine_config["duration_minutes"] + level_config["duration_delta"]

    return {
        "plan_id": f"mr_lim_{selected_key}_{selected_level}",
        "persona": deepcopy(MR_LIM_PERSONA),
        "risk_options": _risk_options(),
        "level_options": _level_options(),
        "selected_risk": {
            "key": selected_key,
            "label": routine_config["label"],
            "description": routine_config["description"],
        },
        "plan_tag": routine_config["plan_tag"],
        "title": routine_config["title"],
        "subtitle": routine_config["subtitle"],
        "level": selected_level,
        "level_label": level_config["label"],
        "duration_minutes": duration_minutes,
        "risk_context": {
            "risk_key": selected_key,
            "top_risk": routine_config["label"],
            "reason": routine_config["reason"],
            "disclaimer": (
                "This routine is general health guidance. It is not medical advice "
                "and does not diagnose or predict individual health outcomes."
            ),
        },
        "exercises": exercises,
        "guidance_tip": {
            "title": "Tip",
            "text": f"{level_config['tip_prefix']} {routine_config['tip']}",
        },
        "safety_note": (
            "Start gently. Stop if you feel chest pain, dizziness, unusual shortness "
            "of breath, or sharp pain."
        ),
        "guideline_note": (
            "Exercise recommendations align with Saranan Aktiviti Fizikal Malaysia "
            "and support SDG3 Good Health and Well-Being."
        ),
        "guideline": {
            "name": "Garis Panduan Aktiviti Fizikal Malaysia",
            "url": "https://infosihat.moh.gov.my/multimedia/garis-panduan/item/garis-panduan-aktiviti-fizikal-malaysia-2.html",
        },
        "source": {
            "name": "wger.de Exercise Database",
            "licence": "CC-BY-SA / open exercise data",
            "usage": (
                "Exercise names, instructions, categories, equipment and media are "
                "wger-sourced where available. Sets, reps, duration and tips are "
                "HealthAge MVP logic. Data is read from Neon when an exercise table "
                "exists, otherwise the app uses the local curated fallback pool."
            ),
        },
    }


def get_replacement_exercise(
    current_id: str | None,
    plan_tag: str = "cardio_core",
    risk_key: str | None = None,
) -> dict[str, Any]:
    """Return a replacement exercise from the same curated MVP pool."""
    selected_key = _normalise_risk_key(risk_key)
    routine_ids = set(RISK_ROUTINES[selected_key]["exercise_ids"])
    preferred_tag = plan_tag or RISK_ROUTINES[selected_key]["plan_tag"]
    if preferred_tag == "cardio_core" and selected_key != DEFAULT_RISK_KEY:
        preferred_tag = RISK_ROUTINES[selected_key]["plan_tag"]
    exercise_pool = _load_exercise_pool()
    candidates = _replacement_candidates(exercise_pool, None, preferred_tag)

    if not candidates:
        candidates = _replacement_candidates(deepcopy(EXERCISE_POOL), None, preferred_tag)

    replacement = _next_replacement_candidate(candidates, current_id, routine_ids)
    if replacement:
        return deepcopy(replacement)

    replacement = _next_replacement_candidate(candidates, current_id, set())
    if replacement:
        return deepcopy(replacement)

    current = _find_exercise_with_tag(exercise_pool, current_id, preferred_tag)
    if current:
        return deepcopy(current)

    raise ValueError(f"No replacement exercise is available for plan tag {preferred_tag}.")


def _load_exercise_pool() -> list[dict[str, Any]]:
    fallback_pool = deepcopy(EXERCISE_POOL)
    database_pool = _database_exercise_pool()
    if not database_pool:
        return fallback_pool

    merged = {exercise["id"]: exercise for exercise in fallback_pool}
    for exercise in database_pool:
        merged[exercise["id"]] = exercise

    ordered = [merged[exercise["id"]] for exercise in fallback_pool if exercise["id"] in merged]
    ordered_ids = {exercise["id"] for exercise in ordered}
    ordered.extend(exercise for exercise in database_pool if exercise["id"] not in ordered_ids)
    return ordered


def _normalise_risk_key(value: str | None) -> str:
    key = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    return RISK_ALIASES.get(key, DEFAULT_RISK_KEY)


def _normalise_level(value: str | None) -> str:
    key = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "low": "beginner",
        "beginner": "beginner",
        "medium": "standard",
        "moderate": "standard",
        "standard": "standard",
        "high": "progress",
        "progress": "progress",
        "advanced": "progress",
    }
    return aliases.get(key, "beginner")


def _risk_options() -> list[dict[str, str]]:
    return [
        {
            "key": key,
            "label": routine["label"],
            "description": routine["description"],
        }
        for key, routine in RISK_ROUTINES.items()
    ]


def _level_options() -> list[dict[str, str]]:
    return [
        {
            "key": key,
            "label": config["label"],
            "description": config["description"],
        }
        for key, config in INTENSITY_LEVELS.items()
    ]


def _scale_exercise_for_level(exercise: dict[str, Any], level_config: dict[str, Any]) -> dict[str, Any]:
    scaled = deepcopy(exercise)
    scaled["sets"] = max(1, _int_or_default(scaled.get("sets"), 1) + level_config["sets_delta"])

    if scaled.get("reps") is not None:
        scaled["reps"] = max(1, _int_or_default(scaled.get("reps"), 1) + level_config["reps_delta"])

    if scaled.get("duration_seconds") is not None:
        scaled["duration_seconds"] = max(
            10,
            _int_or_default(scaled.get("duration_seconds"), 10) + level_config["hold_delta"],
        )

    return scaled


def _select_exercises(exercise_pool: list[dict[str, Any]], exercise_ids: list[str]) -> list[dict[str, Any]]:
    exercise_lookup = {exercise["id"]: exercise for exercise in exercise_pool}
    exercises = [
        deepcopy(exercise_lookup[exercise_id])
        for exercise_id in exercise_ids
        if exercise_id in exercise_lookup
    ]

    if len(exercises) >= 4:
        return exercises[:4]

    selected_ids = {exercise["id"] for exercise in exercises}
    for exercise in exercise_pool:
        if exercise["id"] not in selected_ids:
            exercises.append(deepcopy(exercise))
            selected_ids.add(exercise["id"])
        if len(exercises) == 4:
            break

    return exercises


def _replacement_candidates(
    exercise_pool: list[dict[str, Any]],
    current_id: str | None,
    plan_tag: str,
) -> list[dict[str, Any]]:
    return [
        exercise
        for exercise in exercise_pool
        if exercise["id"] != current_id and plan_tag in exercise["plan_tags"]
    ]


def _next_replacement_candidate(
    candidates: list[dict[str, Any]],
    current_id: str | None,
    blocked_ids: set[str],
) -> dict[str, Any] | None:
    if not candidates:
        return None

    current_index = next(
        (index for index, exercise in enumerate(candidates) if exercise["id"] == current_id),
        -1,
    )
    ordered = candidates[current_index + 1 :] + candidates[: current_index + 1]
    for exercise in ordered:
        if exercise["id"] != current_id and exercise["id"] not in blocked_ids:
            return exercise
    return None


def _find_exercise_with_tag(
    exercise_pool: list[dict[str, Any]],
    exercise_id: str | None,
    plan_tag: str,
) -> dict[str, Any] | None:
    for exercise in exercise_pool:
        if exercise["id"] == exercise_id and plan_tag in exercise["plan_tags"]:
            return exercise
    return None


def _database_exercise_pool() -> list[dict[str, Any]]:
    database = settings.DATABASES.get("default", {})
    if database.get("ENGINE") != "django.db.backends.postgresql":
        return []

    try:
        tables = connection.introspection.table_names()
    except DatabaseError:
        return []

    table_lookup = {table.lower(): table for table in tables}
    table = table_lookup.get("exercise")
    if not table:
        return []

    try:
        rows = _fetch_rows(table)
    except DatabaseError:
        return []

    exercises = [_normalise_exercise_row(row) for row in rows if _row_is_active(row)]
    return [exercise for exercise in exercises if exercise]


def _fetch_rows(table: str) -> list[dict[str, Any]]:
    quoted = connection.ops.quote_name(table)
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {quoted} LIMIT %s", [200])
        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return sorted(
        rows,
        key=lambda row: (
            _int_or_default(row.get("display_order"), 999),
            _int_or_default(row.get("exercise_id"), 999),
            str(row.get("exercise_key") or row.get("exercise_name") or ""),
        ),
    )


def _normalise_exercise_row(row: dict[str, Any]) -> dict[str, Any] | None:
    exercise_key = str(row.get("exercise_key") or "").strip()
    exercise_name = str(row.get("exercise_name") or row.get("name") or "").strip()
    if not exercise_key or not exercise_name:
        return None

    return {
        "id": exercise_key,
        "wger_id": _int_or_none(row.get("wger_id")),
        "wger_uuid": _str_or_none(row.get("wger_uuid")),
        "name": exercise_name,
        "category": str(row.get("category") or "").strip(),
        "equipment": str(row.get("equipment") or "").strip(),
        "muscles": _list_value(row.get("muscles")),
        "sets": _int_or_default(row.get("sets"), 1),
        "reps": _int_or_none(row.get("reps")),
        "duration_seconds": _int_or_none(row.get("duration_seconds")),
        "instructions": str(row.get("instructions") or "").strip(),
        "image_url": _str_or_none(row.get("image_url")),
        "video_url": _str_or_none(row.get("video_url")),
        "source_url": str(row.get("source_url") or "").strip(),
        "source_note": str(row.get("source_note") or "Exercise data is sourced from the HealthAge exercise table.").strip(),
        "difficulty": str(row.get("difficulty_level") or row.get("difficulty") or "beginner").strip(),
        "plan_tags": _list_value(row.get("plan_tags")) or ["cardio_core"],
    }


def _row_is_active(row: dict[str, Any]) -> bool:
    value = row.get("is_active")
    if value is None:
        return True
    return str(value).strip().lower() not in {"0", "false", "no"}


def _list_value(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if text.startswith("["):
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                parsed = []
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        return [item.strip() for item in text.split(",") if item.strip()]
    return [str(value).strip()]


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _int_or_default(value: Any, default: int) -> int:
    return _int_or_none(value) or default


def _str_or_none(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None
