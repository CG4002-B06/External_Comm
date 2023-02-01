def status_has_discrepancy(player, expected_status):
    player_status = player.get_status()
    for key, value in player_status.items():
        if player_status == "shield_time":
            continue
        if expected_status.get(key) != value:
            return True
    return False
