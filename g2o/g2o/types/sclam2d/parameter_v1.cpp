//
// Created by art on 18-07-21.
//

#include "parameter_v1.h"

namespace g2o {
    ParameterV1::ParameterV1() : NodeV1(), Param(), _index(0) {

    }
    bool ParameterV1::read(std::istream& is) {
        std::string interpretation;
        is >> interpretation;
        setInterpretation(interpretation);
        is >> _index;
        return NodeV1::read(is);
    }
    bool ParameterV1::write(std::ostream& os) const {
        os << interpretation() << " " << _index << " ";
        return NodeV1::write(os);
    }
    Vector3 ParameterV1::toVector3() const {
        number_t parameter = estimate();
        number_t filler = 0.0;
        if (interpretation() == "scale") filler = 1.0;
        Vector3 vector = Vector3();
        for (int i = 0; i < 3; i++) vector[i] = filler;
        vector[_index] = parameter;
        return vector;
    }
}