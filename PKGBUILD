# Maintainer: Bryan Kam <archlinux@vo.racio.us>

pkgname=pytc
pkgver=0.2.3
pkgrel=1
pkgdesc='Command-line Twitter client written in Python'
arch=('i686' 'x86_64')
url='http://twitter.com/pythontc'
license=('GPL')
depends=('python2' 'tweepy-git')
makedepends=('git')
optdepends=()
provides=('pytc')
conflicts=('pytc')
# You must run makepkg -g and paste md5sums in here.
source=("pytc-$pkgver.tar.gz::http://gitorious.org/pytc/pytc/archive-tarball/$pkgver")

build() {
  cd "$srcdir/$pkgname-$pkgname"

  python setup.py build
}

package() {
  cd "$srcdir/$pkgname-$pkgname"

  python2 setup.py install --root=$pkgdir
}
