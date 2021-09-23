//
// Created by art on 18-07-21.
//

#include "parameter_v2.h"

namespace g2o {
    ParameterV2::ParameterV2() : NodeV2(), Param(), _index(0) {

    }
    bool ParameterV2::read(std::istream& is) {
        std::string interpretation;
        is >> interpretation;
        setInterpretation(interpretation);
        is >> _index;
        return NodeV2::read(is);
    }
    bool ParameterV2::write(std::ostream& os) const {
        os << interpretation() << " " << _index << " ";
        return NodeV2::write(os);
    }
    Vector3 ParameterV2::toVector3() const {
        Vector2 value = estimate();
        number_t filler = 0.0;
        if (interpretation() == "scale") filler = 1.0;
        switch (_index) {
            case 0: return Vector3(filler, value[0], value[1]);
            case 1: return Vector3(value[0], filler, value[1]);
            case 2: return Vector3(value[0], value[1], filler);
        }
    }
}