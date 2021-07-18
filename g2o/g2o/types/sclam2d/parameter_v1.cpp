//
// Created by art on 18-07-21.
//

#include "parameter_v1.h"

namespace g2o {
    ParameterV1::ParameterV1() : NodeV1(), Param() {

    }
    bool ParameterV1::read(std::istream& is) {
        std::string interpretation;
        is >> interpretation;
        setInterpretation(interpretation);
        return NodeV1::read(is);
    }
    bool ParameterV1::write(std::ostream& os) const {
        os << interpretation() << " ";
        return NodeV1::write(os);
    }
    Vector3 ParameterV1::toVector3(bool inverse) const {
        number_t parameter = estimate();
        if (inverse) {
            parameter = - parameter;
        }
        Vector3 vector = Vector3();
        vector[_index] = parameter;
        return vector;
    }
}