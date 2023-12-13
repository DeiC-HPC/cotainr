## Apparent minimal setup
export SINGULARITYENV_LD_LIBRARY_PATH=\
"/opt/cray/pe/mpich/default/ofi/gnu/9.1/lib-abi-mpich:"\
"/opt/cray/libfabric/1.15.2.0/lib64:"\
"/opt/cray/pe/gcc-libs:"\
"/opt/cray/pe/lib64:"\
"/opt/cray/xpmem/default/lib64:"\
"/usr/lib64"

export SINGULARITY_BIND=\
"/var/spool/slurmd,"\
"/opt/cray,"\
"/usr/lib64/libbrotlicommon.so.1,"\
"/usr/lib64/libbrotlidec.so.1,"\
"/usr/lib64/libcrypto.so.1.1,"\
"/usr/lib64/libcurl.so.4,"\
"/usr/lib64/libcxi.so.1,"\
"/usr/lib64/libgssapi_krb5.so.2,"\
"/usr/lib64/libidn2.so.0,"\
"/usr/lib64/libjansson.so.4,"\
"/usr/lib64/libjitterentropy.so.3,"\
"/usr/lib64/libjson-c.so.3,"\
"/usr/lib64/libk5crypto.so.3,"\
"/usr/lib64/libkeyutils.so.1,"\
"/usr/lib64/libkrb5.so.3,"\
"/usr/lib64/libkrb5support.so.0,"\
"/usr/lib64/liblber-2.4.so.2,"\
"/usr/lib64/libldap_r-2.4.so.2,"\
"/usr/lib64/libnghttp2.so.14,"\
"/usr/lib64/libpcre.so.1,"\
"/usr/lib64/libpsl.so.5,"\
"/usr/lib64/libsasl2.so.3,"\
"/usr/lib64/libssh.so.4,"\
"/usr/lib64/libssl.so.1.1,"\
"/usr/lib64/libunistring.so.2,"\
"/usr/lib64/libzstd.so.1"
