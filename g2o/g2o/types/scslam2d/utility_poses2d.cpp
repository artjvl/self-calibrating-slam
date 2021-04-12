//
// Created by art on 23-03-21.
//

#include "utility_poses2d.h"

namespace g2o {
    namespace utility2d {
        SE2 computePoseDelta(const SE2& p1, const SE2& p2) {
            return p1.inverse() * p2;
        }

        Vector2 computeTranslationDelta(const Vector2& t1, const Vector2& t2) {
            return t2 - t1;
        }

        Rotation2D computeRotationDelta(const Rotation2D& r1, const Rotation2D& r2) {
            return r2.inverse() * r1;
        }

        SE2 scale(const SE2& p, const Vector2& scale) {
            const Vector3 diagonal = Vector3(scale[0], scale[1], 1);
            return SE2(diagonal.asDiagonal() * p.toVector());
        }

        SE2 addOffset(const SE2& p, const SE2& offset) {
            return offset.inverse() * p * offset;
        }

        SE2 addBias(const SE2& p, const SE2& bias) {
            return p * bias;
        }
    }
}
