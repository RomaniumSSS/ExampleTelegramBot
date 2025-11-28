# Plan: Mood Chart Feature

## Objective
Implement a visual mood chart feature (`/moodchart`) that allows users to generate and view a graph of their mood history for a specific period (Day or Week).

## Status
✅ **Completed**

## Steps Executed

1.  **Architecture & Setup**
    -   ✅ Verified `matplotlib` installation.
    -   ✅ Created `src/vibe_tracker_bot/services/charts.py`.

2.  **Backend Logic (Service Layer)**
    -   ✅ Implemented `generate_mood_chart` in `services/charts.py`.
    -   ✅ Used `matplotlib` (with `Agg` backend) to plot `created_at` vs `value`.
    -   ✅ Handled threading with `asyncio.to_thread` to avoid blocking.

3.  **Bot Interface (Handlers)**
    -   ✅ Updated `src/vibe_tracker_bot/handlers/tracking.py`.
    -   ✅ Added `/moodchart` command handler.
    -   ✅ Added inline keyboard for "Day" and "Week".
    -   ✅ Implemented callback handlers for chart generation.
    -   ✅ Added error handling and user feedback ("Рисую график...").

4.  **Testing**
    -   ✅ Verified manual testing by user (confirmed "super").
    -   ✅ Fixed "silent failure" bug by forcing `matplotlib` backend to 'Agg' before import and adding error handling.

## Notes
- Matplotlib backend is set to "Agg" in `services/charts.py` to ensure compatibility with headless environments (like servers or Docker).
- Error handling is robust: if chart generation fails, the user gets a message instead of silence.
