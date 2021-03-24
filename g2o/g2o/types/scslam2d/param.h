//
// Created by art on 24-03-21.
//

#ifndef G2O_PARAM_H
#define G2O_PARAM_H

#include <string>

namespace g2o {
    class Param {
    public:
//        explicit Param(const std::string& type);
        std::string getType() const {
            return _type;
        }
        virtual bool setType(const std::string& type) = 0;

    protected:
        std::string _type;
    };
}



#endif //G2O_PARAM_H
