"""Exercise rules for the pregnancy fitness tracker.

Every statement below comes from one of two sources that were read in full
on 22 October 2026. Nothing here is medical advice.

SOURCES
  [NHS]  NHS, "Exercise in pregnancy"
         https://www.nhs.uk/pregnancy/keeping-well/exercise/
  [CSEP] Mottola MF et al., "2019 Canadian Guideline for Physical Activity
         throughout Pregnancy" (CSEP / SOGC)
         https://csepguidelines.ca/?p=1037

WHAT IS NOT FROM A SOURCE (design choices of this app, labelled as such)
  - The trimester split. Neither source gives different exercise lists per
    trimester. The base advice is the same for every week.
  - "Later pregnancy" in [NHS] has no week number. This app applies the
    "avoid lying flat for more than a few minutes" advice from week 28.
  - The weekly minutes come from what the user logs. The app cannot check
    whether the logged activity was moderate intensity.
"""

SOURCES = [
    {"id": "NHS", "title": "NHS: Exercise in pregnancy",
     "url": "https://www.nhs.uk/pregnancy/keeping-well/exercise/"},
    {"id": "CSEP", "title": "2019 Canadian Guideline for Physical Activity throughout Pregnancy",
     "url": "https://csepguidelines.ca/?p=1037"},
]

DISCLAIMER = (
    "General information only. This is not medical advice. Some conditions "
    "(for example preeclampsia, uncontrolled high blood pressure, placenta previa "
    "after 28 weeks, or unexplained bleeding) mean you should not do strenuous "
    "activity. Ask your midwife or doctor before you start or change your exercise."
)

# Weekly target. [NHS] and [CSEP] both give 150 minutes of moderate activity.
WEEKLY_TARGET_MINUTES = 150
STRENGTH_SESSIONS_PER_WEEK = 2          # [NHS]

# Activities that can count toward the weekly target.
EXERCISES = [
    {"name": "Walking", "source": "NHS"},
    {"name": "Swimming or a water-based pregnancy class", "source": "NHS"},
    {"name": "Yoga", "source": "NHS, CSEP"},
    {"name": "Gentle stretching", "source": "CSEP"},
    {"name": "Muscle-strengthening (for example gym strength training if you already do it)", "source": "NHS, CSEP"},
    {"name": "Pelvic floor muscle training, daily, with proper instruction", "source": "CSEP"},
]

AVOID = [
    {"name": "Sports with a risk of falling or bumping your tummy, such as hockey, rugby or mountain biking", "source": "NHS"},
    {"name": "Scuba diving", "source": "NHS"},
    {"name": "Exercising on an empty stomach", "source": "NHS"},
    {"name": "Starting a new vigorous activity, such as running", "source": "NHS"},
]

TIPS = [
    {"text": "Aim for 150 minutes of moderate activity a week, spread over at least three days.", "source": "NHS, CSEP"},
    {"text": "Include 2 muscle-strengthening sessions a week.", "source": "NHS"},
    {"text": "Moderate means you can talk but not sing.", "source": "NHS"},
    {"text": "Start slowly, for example 10 minutes a day, and build up.", "source": "NHS"},
    {"text": "Drink water, keep cool, and stop if you feel uncomfortable, too hot or unwell.", "source": "NHS"},
    {"text": "If you feel light-headed or nauseous lying flat on your back, change your position.", "source": "CSEP"},
]

LATER_PREGNANCY_WEEK = 28   # app assumption, see module docstring


def trimester(week: int) -> int:
    if week <= 13:
        return 1
    if week <= 27:
        return 2
    return 3


def stage_tips(week: int):
    """Extra tips that depend on the stage. Only statements found in the sources."""
    extra = []
    if week >= LATER_PREGNANCY_WEEK:
        extra.append({"text": "Avoid activities where you lie flat on your back for more than a few minutes.", "source": "NHS"})
        extra.append({"text": "Brisk walking is a good alternative to running.", "source": "NHS"})
        extra.append({"text": "Placenta previa after 28 weeks and a twin pregnancy after week 28 need your care provider's advice before you exercise.", "source": "CSEP"})
    return extra