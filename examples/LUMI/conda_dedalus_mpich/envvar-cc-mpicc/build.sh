mkdir -p $PREFIX/etc/conda/activate.d
mkdir -p $PREFIX/etc/conda/deactivate.d
cp $RECIPE_DIR/envvar_cc_mpicc_activate.sh $PREFIX/etc/conda/activate.d/
cp $RECIPE_DIR/envvar_cc_mpicc_deactivate.sh $PREFIX/etc/conda/deactivate.d/