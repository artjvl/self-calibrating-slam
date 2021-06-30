//
// Created by art on 15-06-21.
//

#ifndef G2O_CONSTRAINT_INFO3_H
#define G2O_CONSTRAINT_INFO3_H

#include "math.h"
#include "g2o/core/base_fixed_sized_edge.h"
#include "info3.h"

namespace g2o {
    class ConstraintInfo3 : public BaseFixedSizedEdge<3, Vector3, Info3> {
    public:
        ConstraintInfo3();

        Vector3 getCovDiagonal() const {
            Vector3 cov = Vector3();
            for (int i = 0; i < cov.size(); i++) {
                cov[i] = pow(_measurement[i], 2);
            }
            return cov;
        }

        Vector3 getInfoDiagonal() const {
            const Vector3& info = getCovDiagonal();
            Vector3 cov = Vector3(0, 0, 0);
            for (int i = 0; i < cov.size(); i++) {
                cov[i] = 1 / info[i];
            }
            return cov;
        }

        void computeError() {
            // variance (from node)
            const Info3* node = static_cast<const Info3*>(_vertices[0]);
            const Vector3& cov_diagonal = node->getCovDiagonal();

            // minimum variance (locally stored)
            const Vector3& min_cov_diagonal = getCovDiagonal();

            // sum
            Vector3 ratios = Vector3();
            double dot = 0.0;
            double determinant = 1.0;
            for (int i = 0; i < 3; i++) {
                ratios[i] = cov_diagonal[i] / min_cov_diagonal[i];
                dot += ratios[i];
                determinant *= ratios[i];
            }
            Vector3 scaled_ratios = Vector3();
            for (int i = 0; i < 3; i++) {
                scaled_ratios[i] = sqrt(_multiplier * fError(determinant) * (ratios[i] / dot));
                if (isinf(scaled_ratios[i]) || isnan(scaled_ratios[i])) {
                    std::cerr << scaled_ratios[i] << std::endl;
                }
            }
            _error = scaled_ratios;
        }

        static double fError(double error) {
            double output = log(error) + 1/(100 * pow(error, 100)) - 0.01;
//            if (output < 0.0) {
//                return 0.0;
//            }
            return output;
        }

        virtual bool read(std::istream& is);
        virtual bool write(std::ostream& os) const;

    protected:
        int _multiplier;
    };
}


#endif //G2O_CONSTRAINT_INFO3_H
