//
// Created by art on 12-04-21.
//

#ifndef G2O_PARAM_H
#define G2O_PARAM_H

#include <string>
#include "g2o/types/slam2d/se2.h"

namespace g2o {
    class Param {
    public:
        virtual std::string getInterpretation() const {
            return _interpretation;
        }
        virtual void setInterpretation(std::string const& interpretation) = 0;
        virtual SE2 composeTransformation(const SE2& transformation, const bool inverse) const = 0;
        virtual SE2 composeTransformation(const SE2& transformation) const {
            return composeTransformation(transformation, false);
        }
    protected:
        std::string _interpretation;
    };
}


#endif //G2O_PARAM_H
