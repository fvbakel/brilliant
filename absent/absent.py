from dataclasses import dataclass
import random
import statistics

@dataclass
class Parameters:

    nr_of_members: int
    nr_of_coaches: int
    nr_of_sick_days: int
    nr_of_vacation_days: int
    nr_typical_vacation_weeks:int
    max_vaction_duration: int
    weeks_per_year:int

params = Parameters(
    nr_of_members   = 9,
    nr_of_coaches   = 2,
    nr_of_sick_days = 2,
    nr_of_vacation_days = 6,
    nr_typical_vacation_weeks = 8,
    max_vaction_duration = 3,
    weeks_per_year = 50)


class AbsentSimulator:

    def __init__(self):
        pass

    def simulate_one_person_one_year(self):
        week_nrs = range(0,params.weeks_per_year)
        high_weeks = range(0,params.nr_typical_vacation_weeks)
        low_weeks = range(params.nr_typical_vacation_weeks,params.weeks_per_year)
        nr_absent = params.nr_of_vacation_days + params.nr_of_sick_days

        base_probability = nr_absent / params.weeks_per_year
        probabilities = []
        for week in high_weeks:
            probabilities.append(base_probability * 2)
        
        for week in low_weeks:
            probabilities.append(base_probability)
        
        absent_weeks = random.choices(population = week_nrs,weights = probabilities,k=nr_absent)
        return set(absent_weeks)

    def simulate_one_year(self):
        weeknr_vs_absent = [0] * params.weeks_per_year
        for person in range(0,params.nr_of_members):
            absent_weeks = self.simulate_one_person_one_year()
            for week_nr in absent_weeks:
                    weeknr_vs_absent[week_nr] = weeknr_vs_absent[week_nr]  + 1

        return weeknr_vs_absent.count(0)

    def simulate_years(self,nr_of_years):
        result = []
        for year in range(0,nr_of_years):
            result.append(self.simulate_one_year())
        
        print(statistics.mean(result))


def main():
    simulator = AbsentSimulator()
    simulator.simulate_years(500)
    

        
if __name__ == '__main__':  
    main()