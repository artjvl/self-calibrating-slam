//
// Created by art on 12-04-21.
//

#ifndef G2O_PARAM_H
#define G2O_PARAM_H

#include <string>

namespace g2o {
    class Param {
    public:
        virtual std::string getInterpretation() {
            return _interpretation;
        }
        virtual void setInterpretation(const std::string interpretation) = 0;
    protected:
        std::string _interpretation;
    };
}


#endif //G2O_PARAM_H
