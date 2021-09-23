//
// Created by art on 18-07-21.
//

#include "parameter_v3.h"

namespace g2o {
    ParameterV3::ParameterV3() : NodeV3(), Param() {

    }
    bool ParameterV3::read(std::istream& is) {
        std::string interpretation;
        is >> interpretation;
        setInterpretation(interpretation);
        return NodeV3::read(is);
    }
    bool ParameterV3::write(std::ostream& os) const {
        os << interpretation() << " ";
        return NodeV3::write(os);
    }
    Vector3 ParameterV3::toVector3() const {
        Vector3 value = estimate();
        return value;
    }
}