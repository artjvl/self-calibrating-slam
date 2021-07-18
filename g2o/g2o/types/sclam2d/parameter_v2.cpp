//
// Created by art on 18-07-21.
//

#include "parameter_v2.h"

namespace g2o {
    ParameterV2::ParameterV2() : NodeV2(), Param() {

    }
    bool ParameterV2::read(std::istream& is) {
        std::string interpretation;
        is >> interpretation;
        setInterpretation(interpretation);
        return NodeV2::read(is);
    }
    bool ParameterV2::write(std::ostream& os) const {
        os << interpretation() << " ";
        return NodeV2::write(os);
    }
    Vector3 ParameterV2::toVector3(bool inverse) const {
        Vector2 value = estimate();
        if (inverse) {
            value = - value;
        }
        return Vector3(value[0], value[1], 0.0);
    }
}