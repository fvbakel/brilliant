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

void Nonogram::line_to_int_array(
    const string &line,
    std::vector<int> *result,
    const char file_delim
) {
    std::istringstream iss(line);
    std::string item;

    while (std::getline(iss, item, file_delim)) {
        char *p;
        int value = (int) strtol(item.c_str(),&p,10);
        if (*p ) {
            cout << "ERROR: Unable to read line: " << line << "\n";
        } else {
            if (value > 0) {
                result->push_back(value);
            }
        }
    }
}

void Nonogram::parse_txt_line(std::string &line,enum direction &cur_dir) {
    vector<int> result;
    const char file_delim = ' ';
    if (line.size() > 0 && line.substr(0,1).compare("#") != 0) {
        line_to_int_array(line,&result,file_delim);

        if (    result.size() > 0 || 
                (result.size() == 0 && line.compare("0") == 0)
        ) {
            MainConstraint *constraint = new MainConstraint(cur_dir,&result);
            main_constraints *p_contraints  = get_constraints(cur_dir);
            p_contraints->push_back(constraint);
        } else {
            cout << "ERROR: Unable to read txt line: " << line << "\n";
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

void Nonogram::parse_non_line(std::string &line,enum direction &cur_dir) {
    vector<int>     result;
    const char file_delim = ',';
    if (line.size() > 0) {

        if (    line.size() > 4 &&
                line.substr(0,4).compare("goal") == 0
        ) {
            m_non_parse_state = searching;
        }

        if (m_non_parse_state == searching) {
            if (line.compare("rows") == 0) {
                m_non_parse_state = parsing_rows;
                cur_dir = y_dir;
            } else if (line.compare("columns") == 0) {
                m_non_parse_state = parsing_cols;
                cur_dir = x_dir;
            } else {
                // ignore this line
            }
        } else {
            
            line_to_int_array(line,&result,file_delim);

            if (    result.size() > 0 || 
                    (result.size() == 0 && line.compare("0") == 0)
            ) {
                MainConstraint *constraint = new MainConstraint(cur_dir,&result);
                main_constraints *p_contraints  = get_constraints(cur_dir);
                p_contraints->push_back(constraint);
            } else {
                cout << "ERROR: Unable to read non line: " << line << "\n";
            }
            result.clear();
        }
    } else if (line.size() == 0) {
        m_non_parse_state = searching;
    }
}

void Nonogram::read_file() {
    if (m_filename != "") {
        string line;
        ifstream input_file;
        enum file_type cur_type = txt_file;
        
        if (m_filename.size() > 4) {
            string extension = m_filename.substr(m_filename.size()-3);
            if (extension.compare("NON") == 0 || extension.compare("non") == 0) {
                cur_type = non_file;
            }
        }

        input_file.open(m_filename);
        if (input_file.is_open()) {
            enum direction cur_dir = x_dir;
            m_x_size = 0;
            m_y_size = 0;
            
            while ( getline(input_file,line)) {
                if (cur_type == non_file) {
                    parse_non_line(line,cur_dir);
                } else {
                    parse_txt_line(line,cur_dir);
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
    m_solving = false;
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
        MainConstraint *constraint = m_x_contraints.at(x_index);
        for (int y_index = 0; y_index < m_y_size; y_index++) {
            Location *location = get_Location(x_index,y_index);
            constraint->add_location(location);
        }
    }

    for (int y_index = 0; y_index < m_y_size; y_index++) {
        MainConstraint *constraint = m_y_contraints.at(y_index);
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
    main_constraints *p_constraints = get_constraints(for_direction);
    for (MainConstraint *constraint : *p_constraints) {
        if (!constraint->is_valid()) {
            printf("Invalid input, to large constraint: ");
            constraint->print();
            return false;
        }
    }
    return true;
}

bool Nonogram::has_dirty_locations() {
    for (Location *location : m_locations ) {
        if (location->is_dirty_any_dir()) {
            return true;
        }
    }
    return false;
}

int Nonogram::get_colored_size_sum(enum direction for_direction,enum color for_color) {
    int sum = 0;
    main_constraints *p_constraints = get_constraints(for_direction);
    for (MainConstraint *constraint : *p_constraints) {
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
    main_constraints *p_constraints = get_constraints(for_direction);
    for (MainConstraint *constraint : *p_constraints) {
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

main_constraints *Nonogram::get_constraints (enum direction for_direction) {
    main_constraints *p_constraints = &m_y_contraints;
    if (for_direction == x_dir) {
        p_constraints = &m_x_contraints;
    }
    return p_constraints;
}

void Nonogram::calc_constraint_solutions (enum direction for_direction) {
    main_constraints *p_constraints = get_constraints(for_direction);
    for (MainConstraint *constraint : *p_constraints) {
        constraint->calculate_solutions();
    }
}

void Nonogram::lock_constraint_solutions (
        enum direction for_direction
    ) {
    main_constraints *p_constraints = get_constraints(for_direction);
    for (MainConstraint *constraint : *p_constraints) {
        if (constraint->get_solution_size() > 0) {
            constraint->calc_locks();
        }
    }
}

int Nonogram::reduce_constraint_solutions (
        enum direction for_direction
    ) {
    int nr_reduced = 0;
    main_constraints *p_constraints = get_constraints(for_direction);

    for (MainConstraint *constraint : *p_constraints) {
        if (constraint->get_nr_dirty() > 0) {
            if (constraint->get_solution_size() > 1) {
                nr_reduced += constraint->reduce_solutions();
            }
            constraint->clear_dirty();
        }
    }
    return nr_reduced;
}

void Nonogram::calc_and_lock_constraints (
        enum direction for_direction
    ) {
    int nr_reduced = 0;
    main_constraints *p_constraints = get_constraints(for_direction);

    for (MainConstraint *constraint : *p_constraints) {
        if (constraint->get_nr_dirty() > 0) {
            if (constraint->get_solution_size() > 1) {
                nr_reduced = constraint->reduce_solutions();
                constraint->clear_dirty();
                if (nr_reduced > 0 ) {
                    constraint->calc_locks();
                }
            } else if (constraint->get_solution_size() == 0) {
                constraint->clear_dirty();
                constraint->calc_locks_rules();
            } else {
                constraint->clear_dirty();
            }
        }
    }
}

MainConstraint *Nonogram::get_next_to_calculate() {
    MainConstraint *next_constraint_x = nullptr;
    MainConstraint *next_constraint_y = nullptr;
    next_constraint_x = get_next_to_calculate_dir(x_dir);
    next_constraint_y = get_next_to_calculate_dir(y_dir);
    if (next_constraint_x== nullptr && next_constraint_y == nullptr) {
        return nullptr;
    } else if (next_constraint_x== nullptr ) {
        return next_constraint_y;
    } else if (next_constraint_y== nullptr ) {
        return next_constraint_x;
    } else {
        int x_var_size = next_constraint_x->get_variation();
        int y_var_size = next_constraint_y->get_variation();
        if (x_var_size < y_var_size) {
            return next_constraint_x;
        } else {
            return next_constraint_y;
        }
    }
}

MainConstraint *Nonogram::get_next_to_calculate_dir(enum direction for_direction) {
    MainConstraint *next_constraint = nullptr;
    main_constraints *p_constraints = get_constraints(for_direction);
    int smallest_variation = -1;
    for (MainConstraint *constraint : *p_constraints) {
        if (constraint->get_solution_size() == 0) {
            int variation = constraint->get_variation();
            
            if (    smallest_variation == -1 ||
                    variation < smallest_variation
            ) {
                smallest_variation = variation;
                next_constraint = constraint;
            }
        }
    }
    return next_constraint;
}

enum direction Nonogram::swap_direction(enum direction cur_dir) {
    if (cur_dir == x_dir) {
        return y_dir;
    } else {
        return x_dir;
    }
}

void Nonogram::apply_solutions_and_rules() {
    enum direction cur_dir = y_dir;

    MainConstraint *constraint = get_next_to_calculate();
    while (constraint != nullptr) {
        constraint->calculate_solutions();
        if (m_rule_improve_log) {
            rule_improve_log(constraint);
        }
        constraint->calc_locks();
        cur_dir = constraint->get_direction();
        cur_dir = reduce_and_lock(cur_dir);
        
        constraint = get_next_to_calculate();
    }

    cur_dir = reduce_and_lock(cur_dir);
}

void Nonogram::apply_rules_only() {
    for (MainConstraint *constraint : m_x_contraints) {
        constraint->calc_locks_rules();
    }
    for (MainConstraint *constraint : m_y_contraints) {
        constraint->calc_locks_rules();
    }
    reduce_and_lock(x_dir);
}

enum direction Nonogram::reduce_and_lock (
            enum direction cur_dir
) {
    while (has_dirty_locations()) {
        cur_dir = swap_direction(cur_dir);
        calc_and_lock_constraints(cur_dir);
    }
    return cur_dir;
}

bool Nonogram::solve() {
    if (m_solving == false) {
        m_solving = true;
        if (!is_input_valid()) {
            return false;
        }

        apply_rules_only();
        if (is_solved()) {
            printf("Solved with rules only.\n");
            return true;
        } else {
            printf("Solve with rules only ready, solve the remaining with solutions reduction and rules.\n");
        }

        try {
            apply_solutions_and_rules();
        } catch (std::domain_error &e) {
            std::cout << e.what() << "\n"; 
            std::cout << "Unable to solve.\n";
            return false;
        }
        if (is_solved()) {
            printf("Solved with rules and constraints only.\n");
            return true;
        } else {
            printf("Solve with solution reduction and rules ready, solve the remaining with backtracking.\n");
        }
    }

    return solve_constraint_backtrack();
}

bool Nonogram::solve_constraint_backtrack(int con_idx) {
    bool result = false;

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

void Nonogram::enable_rule_improve_log() {
    m_rule_improve_log =true;
}

void Nonogram::rule_improve_log(Constraint *constraint) {
    std::string before = constraint->loc_string();
    constraint->calc_locks();
    std::string after = constraint->loc_string();
    if ( before.compare(after) != 0) {
        std::cout << "Possible rule improvement Given: ";
        std::cout << constraint->clue_string() << " [";
        std::cout << before << "] expected: [";
        std::cout << after << "]\n\n";
    }
}

Nonogram::~Nonogram() {
    for (MainConstraint* constraint : m_x_contraints) {
        delete constraint;
    }
    m_x_contraints.clear();

    for (MainConstraint* constraint : m_y_contraints) {
        delete constraint;
    }
    m_y_contraints.clear();

    for (Location *location : m_locations) {
        delete location;
    }
    m_locations.clear();

}