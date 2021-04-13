//
// Created by art on 12-04-21.
//

#ifndef G2O_PARAM_SE2_H
#define G2O_PARAM_SE2_H

#include "node_se2.h"
#include "param.h"

namespace g2o {
    class ParamSE2 : public NodeSE2, public Param {
    public:
        ParamSE2();
        void setInterpretation(std::string const& interpretation);
        SE2 composeTransformation(const SE2& transformation, const bool inverse) const;
        virtual bool read(std::istream& is);
        virtual bool write(std::ostream& os) const;
    };
}

#endif //G2O_PARAM_SE2_H
