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
        virtual SE2 composeTransformation(const SE2& transformation, const bool inverse) const = 0;
        virtual SE2 composeTransformation(const SE2& transformation) const {
            return composeTransformation(transformation, false);
        }
    };
}


#endif //G2O_PARAM_H
