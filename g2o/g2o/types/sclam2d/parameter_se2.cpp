//
// Created by art on 18-07-21.
//

#include "parameter_se2.h"

namespace g2o {
    ParameterSE2::ParameterSE2() : NodeSE2() {

    }
    bool ParameterSE2::read(std::istream& is) {
        std::string interpretation;
        is >> interpretation;
        setInterpretation(interpretation);
        return NodeSE2::read(is);
    }
    bool ParameterSE2::write(std::ostream& os) const {
        os << interpretation() << " ";
        return NodeSE2::write(os);
    }
    Vector3 ParameterSE2::toVector3(bool inverse) const {
        SE2 value = estimate();
        if (inverse) {
            value = value.inverse();
        }
        return value.toVector();
    }
}