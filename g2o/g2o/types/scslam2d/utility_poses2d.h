//
// Created by art on 23-03-21.
//

#ifndef G2O_UTILITY_POSES2D_H
#define G2O_UTILITY_POSES2D_H

#include "../slam2d/se2.h"

namespace g2o {
    namespace utility2d {
        SE2 computePoseDelta(const SE2& p1, const SE2& p2);

        Vector2 computeTranslationDelta(const Vector2& t1, const Vector2& t2);

        Rotation2D computeRotationDelta(const Rotation2D& r1, const Rotation2D& r2);

        SE2 scale(const SE2& p, const Vector2& scale);

        SE2 addOffset(const SE2& p, const SE2& offset);

        SE2 addBias(const SE2& p, const SE2& bias);
    }
}

#endif //G2O_UTILITY_POSES2D_H
