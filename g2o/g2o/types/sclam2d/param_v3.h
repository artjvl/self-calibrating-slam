//
// Created by art on 12-04-21.
//

#ifndef G2O_PARAM_V3_H
#define G2O_PARAM_V3_H

#include "node_v3.h"
#include "param.h"

namespace g2o {
    class ParamV3 : public NodeV3, public Param {
    public:
        ParamV3();
        void setInterpretation(std::string const& interpretation);
        SE2 composeTransformation(const SE2& transformation, const bool inverse) const;
        virtual bool read(std::istream& is);
        virtual bool write(std::ostream& os) const;
    };
}


#endif //G2O_PARAM_V3_H
