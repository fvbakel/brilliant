#include <iostream>
#include <fstream>
#include <sstream>

#include <Nonogram.h>
#include <Piece.h>

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

        } else {
            cout << "ERROR: Unable to open file: " << m_filename << "\n";
        }
    }
}

void Nonogram::reset() {
    for (Location *location : m_locations) {
        location->set_piece(nullptr);
    }
}

/*
void Nonogram::fill_sizes() {
    m_x_size = m_x_contraints.size();
    m_y_size = m_y_contraints.size();

    for (Constraint *constraint : m_x_contraints) {
        constraint->set_size(m_y_size);
    }
    for (Constraint *constraint : m_y_contraints) {
        constraint->set_size(m_x_size);
    }
}
*/

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


bool Nonogram::is_solved() {
    return is_consistent() && is_complete();
}

bool Nonogram::is_consistent() {
    for (Constraint *constraint : m_x_contraints) {
        if (!constraint->is_passed()) {
//            constraint->print();
            return false;
        }
    }
//    printf("X-passed\n");
    for (Constraint *constraint : m_y_contraints) {
        if (!constraint->is_passed()) {
//            constraint->print();
            return false;
        }

    }
//     printf("Y-passed\n");
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
    if (location_index < m_locations.size()) {
        int next_location = location_index + 1;
        for (int piece_index = 0; piece_index < 2; piece_index++) {
            m_locations[location_index]->set_piece(m_pieces[piece_index]);

    //        printf("Checking solution:\n");
    //        print();

            if (is_consistent()) {
    //            printf("Still consistent\n");
                result = solve_location_backtrack(next_location);
                if (result) {
                    return result;
                }
            }
    //        printf("Solution not ok\n");
            m_locations[location_index]->set_piece(nullptr);
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

    delete m_pieces[0];
    delete m_pieces[1];
}