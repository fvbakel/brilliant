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

Nonogram::~Nonogram() {
    for (Constraint* constraint : m_x_contraints) {
        delete constraint;
    }
    m_x_contraints.clear();

    for (Constraint* constraint : m_y_contraints) {
        delete constraint;
    }
    m_y_contraints.clear();
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
        } else {
            cout << "ERROR: Unable to open file: " << m_filename << "\n";
        }
    }
}