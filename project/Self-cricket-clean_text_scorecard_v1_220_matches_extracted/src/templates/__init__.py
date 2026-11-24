"""Template library for cricket commentary generation. 8 narrative phases."""
from src.templates.phase_1_setting import PHASE_1_TEMPLATES
from src.templates.phase_2_early_innings import PHASE_2_TEMPLATES
from src.templates.phase_3_middle_innings import PHASE_3_TEMPLATES
from src.templates.phase_4_late_innings import PHASE_4_TEMPLATES
from src.templates.phase_5_bowling_summary import PHASE_5_TEMPLATES
from src.templates.phase_6_chase_start import PHASE_6_TEMPLATES
from src.templates.phase_7_chase_middle import PHASE_7_TEMPLATES
from src.templates.phase_8_finish import PHASE_8_TEMPLATES

ALL_PHASE_TEMPLATES = {
    1: PHASE_1_TEMPLATES,
    2: PHASE_2_TEMPLATES,
    3: PHASE_3_TEMPLATES,
    4: PHASE_4_TEMPLATES,
    5: PHASE_5_TEMPLATES,
    6: PHASE_6_TEMPLATES,
    7: PHASE_7_TEMPLATES,
    8: PHASE_8_TEMPLATES,
}
