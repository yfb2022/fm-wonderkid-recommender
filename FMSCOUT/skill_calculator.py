from abc import ABC, abstractmethod


class SkillCalculator(ABC):
    @abstractmethod
    def calculate(self, player_data):
        """
        :param player_data: 
        :return: list : calculated stat
        """
        pass


class FieldPlayerSkillCalculator(SkillCalculator):
    def calculate(self, youth):
        defending = youth['Tackling'] * 0.5 + youth['Marking'] * 0.25 + youth['Positioning'] * 0.25
        physical = youth['Strength'] * 0.25 + youth['Stamina'] * 0.25 + youth['Balance'] * 0.25 + youth[
            'Agility'] * 0.25
        speed = youth['Acceleration'] * 0.5 + youth['Pace'] * 0.5
        vision = youth['Vision'] * 0.33 + youth['Flair'] * 0.33 + youth['Passing'] * 0.34
        attacking = youth['Finishing'] * 0.34 + youth['Off The Ball'] * 0.33 + youth['Composure'] * 0.33
        technique = youth['Technique'] * 0.34 + youth['First Touch'] * 0.33 + youth['Dribbling'] * 0.33
        aerial = youth['Heading'] * 0.5 + youth['Jumping Reach'] * 0.5
        mental = (youth['Determination'] + youth['Decision'] + youth['Anticipation'] +
                  youth['Teamwork'] + youth['Bravery'] + youth['Concentration']) * 0.166
        return [defending, physical, speed, vision, attacking, technique, aerial, mental]


class GKSkillCalculator(SkillCalculator):
    def calculate(self, youth):
        distribution = youth['Passing'] * 0.25 + youth['Vision'] * 0.25 + youth['Kicking(GK)'] * 0.25 + youth[
            'Throwing(GK)'] * 0.25
        eccentricity = youth['Aggression'] * 0.2 + youth['Eccentricity(GK)'] * 0.8
        mental = (youth['Anticipation'] + youth['Bravery'] + youth['Concentration'] +
                  youth['Determination'] + youth['Teamwork'] + youth['Decision']) * 0.166
        shot_stopping = youth['Reflexes(GK)'] * 0.3 + youth['One On Ones(GK)'] * 0.3 + youth['Handling(GK)'] * 0.2 + \
                        youth['Punching(GK)'] * 0.2
        physical = youth['Agility'] * 0.3 + youth['Balance'] * 0.2 + youth['Natural Fitness'] * 0.2 + \
                   youth['Work Rate'] * 0.2 + youth['Stamina'] * 0.1
        speed = youth['Rushing Out(GK)'] * 0.6 + youth['Pace'] * 0.4
        aerial = youth['Aerial Reach(GK)'] * 0.8 + youth['Jumping Reach'] * 0.2
        communication = youth['Communication(GK)'] * 0.7 + youth['Command Of Area(GK)'] * 0.3
        return [distribution, eccentricity, mental, shot_stopping, physical, speed, aerial, communication]
