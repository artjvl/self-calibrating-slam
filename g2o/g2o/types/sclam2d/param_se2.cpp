//
// Created by art on 12-04-21.
//

#include "param_se2.h"

namespace g2o {
    ParamSE2::ParamSE2() : NodeSE2() {
    }

    void ParamSE2::setInterpretation(std::string const& interpretation) {
        if (interpretation == "BIAS" || interpretation == "OFFSET") {
            _interpretation = interpretation;
        }
    }

    SE2 ParamSE2::composeTransformation(const SE2& transformation, const bool inverse) const {
        SE2 parameter = estimate();
        if (inverse) {
            parameter = parameter.inverse();
        }

        assert (_interpretation == "BIAS" || _interpretation == "OFFSET");
        if (_interpretation == "BIAS") {
            return transformation * parameter;
        } else {
            return parameter * transformation * parameter.inverse();
        }
    };

    bool ParamSE2::read(std::istream& is) {
        std::string interpretation;
        is >> interpretation;
        setInterpretation(interpretation);
        return NodeSE2::read(is);
    }

    bool ParamSE2::write(std::ostream& os) const {
        os << getInterpretation() << " ";
        return NodeSE2::write(os);
    }
}