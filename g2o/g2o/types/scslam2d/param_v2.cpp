//
// Created by art on 23-03-21.
//

#include "param_v2.h"

namespace g2o {
    ParamV2::ParamV2() : NodeV2() {
    }

    bool ParamV2::setType(const std::string& type) {
        if (type == "SCALE") {
            _type = type;
        return true;
    }
    return false;
    }
}
