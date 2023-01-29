def status_has_discrepancy(players, expected_status):
    for player in players:
        player_status = player.get_status()
        for key, value in player_status:
            if expected_status.get(key) != value:
                return True
    return False
