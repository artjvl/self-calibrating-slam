//
// Created by art on 12-04-21.
//

#include "param_v3.h"

namespace g2o {
    ParamV3::ParamV3() : NodeV3() {
    }

    void ParamV3::setInterpretation(std::string const& interpretation) {
        if (interpretation == "SCALE") {
            _interpretation = interpretation;
        }
    }

    SE2 ParamV3::composeTransformation(const SE2& transformation, const bool inverse) const {
        Vector3 parameter = estimate();
        if (inverse) {
            parameter = - parameter;
        }

        assert (_interpretation == "SCALE");
        return SE2(parameter.asDiagonal() * transformation.toVector());
    }

    bool ParamV3::read(std::istream& is) {
        std::string interpretation;
        is >> interpretation;
        setInterpretation(interpretation);
        return NodeV3::read(is);
    }

    bool ParamV3::write(std::ostream& os) const {
        os << getInterpretation() << " ";
        return NodeV3::write(os);
    }
}