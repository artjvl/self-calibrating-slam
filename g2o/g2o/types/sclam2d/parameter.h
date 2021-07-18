//
// Created by art on 18-07-21.
//

#ifndef G2O_PARAMETER_H
#define G2O_PARAMETER_H

#include <string>
#include <g2o/core/eigen_types.h>

namespace g2o {
    class Param {
    public:
        Param();
        std::string interpretation() const {
            return _interpretation;
        }
        void setInterpretation(std::string const& interpretation) {
            _interpretation = interpretation;
        }
        virtual Vector3 toVector3(bool inverse) const = 0;
        virtual Vector3 toVector3() const {
            return toVector3(false);
        }
    protected:
        std::string _interpretation;
    };
}

#endif //G2O_PARAMETER_H