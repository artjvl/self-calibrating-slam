//
// Created by art on 23-03-21.
//

#include "param_se2.h"

namespace g2o {
    ParamSE2::ParamSE2() : NodeSE2() {
    }

    bool ParamSE2::setType(const std::string &type) {
       if (type == "OFFSET" || type == "BIAS") {
            _type = type;
            return true;
        }
        return false;
    }
}
