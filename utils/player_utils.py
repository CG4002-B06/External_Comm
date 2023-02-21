def status_has_discrepancy(player, expected_status):
    player_status = player.get_status(need_shield_time=False)
    for key, value in player_status.items():
        if expected_status.get(key) != value:
            print(f"{key} mismatches, expected: {expected_status.get(key)}, actual:{value}")
            return True
    return False
