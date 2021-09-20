#include <iostream>
#include <fstream>
#include <sstream>

#include <Nonogram.h>

Nonogram::Nonogram() {
    return;
}

Nonogram::Nonogram(const string &filename) {
    m_filename = string(filename);
    this->read_file();
}

void Nonogram::line_to_int_array(const string &line,std::vector<int> *result) {
    std::istringstream iss(line);
    std::string item;

    while (std::getline(iss, item, FILE_DELIM)) {
        int value = stoi(item);
        if (value > 0) {
            result->push_back(value);
        }
    }
}

void Nonogram::read_file() {
    if (m_filename != "") {
        string line;
        vector<int> result;
        ifstream input_file;
        input_file.open(m_filename);
        if (input_file.is_open()) {
            enum direction cur_dir = x_dir;
            m_x_size = 0;
            m_y_size = 0;
            
            while ( getline(input_file,line)) {
                if (line.size() > 0 && line.substr(0,1).compare("#") != 0) {
                    line_to_int_array(line,&result);

                    if (result.size() > 0) {
                        Constraint *constraint = new Constraint(cur_dir,&result);
                        if (cur_dir == x_dir) {
                            m_x_contraints.push_back(constraint);
                        } else {
                            m_y_contraints.push_back(constraint);
                        }
                    } else {
                        cout << "ERROR: Unable to read line: " << line << "\n";
                    }
                    result.clear();

                } else if (line.size() == 0) {
                    if (cur_dir == x_dir) {
                        cur_dir = y_dir;
                    } else {
                        cout << "Warning: More than one empty line\n";
                    }
                }
            }
            input_file.close();

            m_x_size = m_x_contraints.size();
            m_y_size = m_y_contraints.size();
            create_locations();

            if (!is_input_valid()) {
                cout << "ERROR: Invalid input: " << m_filename << "\n";
            }

        } else {
            cout << "ERROR: Unable to open file: " << m_filename << "\n";
        }
    }
}

void Nonogram::reset() {
    m_sol_calcs.clear();
    for (Location *location : m_locations) {
        location->hard_reset();
    }

}

void Nonogram::create_locations() {
    for (int x_index = 0; x_index < m_x_size; x_index++) {
        for (int y_index = 0; y_index < m_y_size; y_index++) {
            m_locations.push_back(new Location(x_index, y_index));
        }    
    }

    for (int x_index = 0; x_index < m_x_size; x_index++) {
        Constraint *constraint = m_x_contraints.at(x_index);
        for (int y_index = 0; y_index < m_y_size; y_index++) {
            Location *location = get_Location(x_index,y_index);
            constraint->add_location(location);
        }
    }

    for (int y_index = 0; y_index < m_y_size; y_index++) {
        Constraint *constraint = m_y_contraints.at(y_index);
        for (int x_index = 0; x_index < m_x_size; x_index++) {
            Location *location = get_Location(x_index,y_index);
            constraint->add_location(location);
        }
    }
}

Location* Nonogram::get_Location(const int x, const int y) {
    if (x < m_x_size && y < m_y_size) {
        int index = x + y * m_x_size;
        return m_locations.at(index);
    } else {
        printf("ERROR: Location %d,%d does not exists.\n", x, y);
        return nullptr;
    }
}

bool Nonogram::is_input_valid() {
    if (!m_valid_checked) {
        bool dir_valid = is_input_valid_dir(x_dir) && is_input_valid_dir(y_dir);
        bool sum_valid = true;
        
        int x_black_sum =get_colored_size_sum(x_dir,black);
        int y_black_sum =get_colored_size_sum(y_dir,black);

        if (x_black_sum != y_black_sum) {
            printf("Invalid input, total nr of black (%d) in horizontal does march vertical(%d).\n",
                x_black_sum,y_black_sum);
            sum_valid = false;
        }
        m_valid_checked = true;
        m_valid = dir_valid && sum_valid;
    } 

    return m_valid;
}
bool Nonogram::is_input_valid_dir(enum direction for_direction) {
    constraints *p_constraints = get_constraints(for_direction);
    for (Constraint *constraint : *p_constraints) {
        if (!constraint->is_valid()) {
            printf("Invalid input, to large constraint: ");
            constraint->print();
            return false;
        }
    }
    return true;
}

int Nonogram::get_colored_size_sum(enum direction for_direction,enum color for_color) {
    int sum = 0;
    constraints *p_constraints = get_constraints(for_direction);
    for (Constraint *constraint : *p_constraints) {
        sum += constraint->get_colored_size(for_color);
    }
    return sum;
}

bool Nonogram::is_solved() {
    return is_consistent() && is_complete();
}

bool Nonogram::is_consistent() {
    return is_consistent_dir(x_dir) && is_consistent_dir(y_dir);
}

bool Nonogram::is_consistent_dir(enum direction for_direction) {
    constraints *p_constraints = get_constraints(for_direction);
    for (Constraint *constraint : *p_constraints) {
        if (!constraint->is_passed()) {
            return false;
        }
    }
    return true;
}

bool Nonogram::is_complete() {
    bool complete = true;
    for (Location *location : m_locations) {
        if (!location->is_solved()) {
            complete = false;
            break;
        }
    }
    return complete;
}

void Nonogram::print() {
    printf("\n");
    for (int y_index = 0; y_index < m_y_size; y_index++) {
        for (int x_index = 0; x_index < m_x_size; x_index++) {
            Location *location = get_Location(x_index, y_index);
            location->print();
        }
        printf("\n");
    }

}

bool Nonogram::solve_location_backtrack(int location_index) {
    bool result = false;
    if (!is_input_valid()) {
        return false;
    }
    if (location_index < m_locations.size()) {
        int next_location = location_index + 1;
        for (int color_index = 0; color_index < 2; color_index++) {
            m_locations[location_index]->set_color(m_colors[color_index]);

            if (is_consistent()) {
                result = solve_location_backtrack(next_location);
                if (result) {
                    return result;
                }
            }
            m_locations[location_index]->set_color(no_color);
        }
    } else {
        result = true;
    }
    return result;
}

constraints *Nonogram::get_constraints (enum direction for_direction) {
    constraints *p_constraints = &m_y_contraints;
    if (for_direction == x_dir) {
        p_constraints = &m_x_contraints;
    }
    return p_constraints;
}

void Nonogram::calc_constraint_solutions (enum direction for_direction) {
    constraints *p_constraints = get_constraints(for_direction);
    for (Constraint *constraint : *p_constraints) {
        constraint->calculate_solutions();
    }
    m_sol_calcs.insert(for_direction);
}

void Nonogram::lock_constraint_solutions (
        enum direction for_direction,
        std::unordered_set<int> *affected
    ) {
    constraints *p_constraints = get_constraints(for_direction);
    for (Constraint *constraint : *p_constraints) {
        constraint->calc_locks(affected);
    }
}

int Nonogram::reduce_constraint_solutions (
        enum direction for_direction,
        std::unordered_set<int> *affected
    ) {
    int nr_reduced = 0;
    constraints *p_constraints = get_constraints(for_direction);

    for (int i : *affected) {
        Constraint *constraint = (*p_constraints)[i];
        nr_reduced += constraint->reduce_solutions();
    }
    return nr_reduced;
}

void Nonogram::init_constraint_solutions_1() {
    std::unordered_set<int> affected;
    enum direction cur_dir = y_dir;
    calc_constraint_solutions(cur_dir);
    lock_constraint_solutions(cur_dir,&affected);
    affected.clear();

    cur_dir = x_dir;
    calc_constraint_solutions(cur_dir);
    lock_constraint_solutions(cur_dir,&affected);
    while (affected.size() > 0) {
        if (cur_dir == x_dir) {
            cur_dir = y_dir;
        } else {
            cur_dir = x_dir;
        }
        int nr_reduced = reduce_constraint_solutions(cur_dir,&affected);
        affected.clear();
        
        if (nr_reduced > 0) {
            lock_constraint_solutions(cur_dir,&affected);
        }
    }
}

bool Nonogram::solve_constraint_backtrack(int con_idx) {
    bool result = false;
    if (con_idx == 0 && m_sol_calcs.size() == 0) {
        if (!is_input_valid()) {
            return false;
        }
        init_constraint_solutions_1();
        if (is_solved()) {
            printf("Solved with constraints only.\n");
            return true;
        } else {
            printf("Constraints init ready, solve the remaining with backtracking.\n");
        }
    }

    if (con_idx < m_y_contraints.size()) {
        int nxt_con_idx = con_idx + 1;
        for (int sol_idx = 0; sol_idx < m_y_contraints[con_idx]->get_solution_size(); sol_idx++) {
            m_y_contraints[con_idx]->set_solution(sol_idx);

            if (is_consistent_dir(x_dir)) {
                result = solve_constraint_backtrack(nxt_con_idx);
                if (result) {
                    return result;
                }
            }
            m_y_contraints[con_idx]->reset_solution();
        }
        
    } else {
        result = true;
    }
    return result;
}

Nonogram::~Nonogram() {
    for (Constraint* constraint : m_x_contraints) {
        delete constraint;
    }
    m_x_contraints.clear();

    for (Constraint* constraint : m_y_contraints) {
        delete constraint;
    }
    m_y_contraints.clear();

    for (Location *location : m_locations) {
        delete location;
    }
    m_locations.clear();

}