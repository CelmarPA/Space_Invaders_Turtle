class CheckHit:
    @staticmethod
    def check_collision(laser, ship, threshold):
        """
        Checks if two Turtle objects are close enough to count as a collision.

        :param laser: a Turtle object representing the laser.
        :param ship: a Turtle object representing the ship.
        :param threshold: distance below which a collision is registered.

        :return: True if laser and ship are within the threshold distance.
        """

        return laser.distance(ship) < threshold

    @staticmethod
    def check_lasers_vs_targets(lasers, targets, threshold = 20):
        """
        Check collisions between lasers and targets.

        :param lasers: List of laser objects (either player or enemy).
        :param targets: List of Turtle-based objects to check for hits.
        :param threshold: Distance to consider a hit.

        :return: List of (laser, target) pairs that collided.
        """

        hits = []
        hit_targets = set()    # Prevents multiple lasers from hitting the same target in a single frame

        for laser in lasers:
            if not laser.active:
                continue        # Skip inactive lasers

            for target in targets:
                if target in hit_targets:
                    continue    # Target already hit, skip it

                if target.distance(laser) < threshold:
                    hits.append((laser, target))
                    hit_targets.add(target)
                    break       # One laser can only hit one target

        return hits

    @staticmethod
    def check_laser_vs_laser(player_lasers, enemy_lasers):
        """
        Checks for collisions between player lasers and enemy lasers.
        Useful for mutual destruction (e.g., midair laser clashes).

        :param player_lasers: list of Turtle-based player lasers.
        :param enemy_lasers: list of Turtle-based enemy lasers.

        :return: List of (player_laser, enemy_laser) pairs that collided.
        """

        hits = []

        for p_laser in player_lasers:
            if not p_laser.active:
                continue
            for e_laser in enemy_lasers:
                if not e_laser.active:
                    continue

                # Check distance between lasers (adjust threshold according to laser size)
                if p_laser.distance(e_laser) < 10:
                    hits.append((p_laser, e_laser))
                    break       # A player laser can hit only one enemy laser

        return hits
