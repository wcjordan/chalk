"""
Constant values for todo reordering rebalancing
"""
import math

# Use a larger initial step in anticipation of reordering to the top being
# common
RANK_ORDER_INITIAL_STEP = math.pow(2, 60)
RANK_ORDER_DEFAULT_STEP = math.pow(2, 45)
RANK_ORDER_MAX = math.pow(2, 63) - 1
