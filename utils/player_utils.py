def status_has_discrepancy(player, expected_status):
    player_status = player.get_status()
    player_status.pop("shield_time")
    for key, value in player_status.items():
        if expected_status.get(key) != value:
            return True
    return False
