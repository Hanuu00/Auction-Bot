declare global {
  interface Window {
    kakao: any;
  }
}

export const loadKakaoMap = () => {
  return new Promise((resolve) => {
    if (window.kakao?.maps) {
      resolve(true);
      return;
    }

    const script = document.createElement('script');
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${process.env.NEXT_PUBLIC_KAKAO_APP_KEY}&libraries=services,clusterer&autoload=false`;
    script.onload = () => {
      window.kakao.maps.load(() => resolve(true));
    };

    document.head.appendChild(script);
  });
};
