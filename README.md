# WorldOfConnect6


육목 알고리즘 대회를 위한 웹 기반 플랫폼 
 

문제 정의

AI 육목 경진대회에서 사용할 수 있는 웹 기반의 플랫폼으로, 육목 알고리즘 대회 진행을 위한 플레이어, 진행자, 그리고 관람자들을 위한 서비스이다. 육목이란, 오목을 개량하여 돌을 연속하여 여섯개 돌을 먼저 놓는 사람이 이기는 게임이다.
기존에 대회 진행을 시각화하기 위해 직접 바둑판에 돌을 두어야 하는 것의 불편함을 해결하고자 하였으며, 소스코드 파일을 대회 서버에 업로드 해서 게임을 진행할 때 대회 참여자의 컴퓨팅 자원 활용이 불가능하다는 단점을 해결하고자 기획하였다.
게임 진행에 필요한 API를 제공하고 웹 인터페이스로 실시간으로 중계가 가능하도록 구현하였다. 또한 내장된 알고리즘으로 서버와의 연습 경기를 할 수 있도록 제공한다.



주요 기능

Back-end는 Django 프레임워크, 데이터베이스는 sqlite3를 사용하였다. Front-end 는 Angular로 개발되었고, Apache 웹 서버를 통해 application을 최종적으로 플랫폼 서비스를 구축하였다.

메인 페이지에서는 게임 규칙과 플레이어 API와 예제 코드를 확인할 수 있다. 아래 세 버튼을 통해 세 가지 핵심적인 서비스를 제공한다. 육목 알고리즘 대회를 위한 2인용 대국, 내장된 서버 알고리즘과 연습이 가능한 1인용 대국이 가능하도록 구축하였다. 또한 참가자가 아니더라도, 대회 정보를 알고 있다면 누구나 실시간 관전이 가능하다.

- 대회 진행자는 ‘대국 만들기 (2인용)’ 버튼을 클릭하여 대국 참가자 2명에 대한 정보를 입력한다. 이 때, Room name은 다른 대국과 구별되도록 고유한 이름만 등록이 가능하다.
- 대국 정보 등록 후 가이드 페이지가 제공된다. 대회 진행자는 여기서 제공되는 Player code를 가지고 대회 참가자들이 게임을 진행이 가능하도록 안내한다.
- 대회 참가자들은 player code와 제공된 API를 자신의 육목 알고리즘에 적용하여 대국을 진행한다. 이 때, 규칙에 따라 적돌이 임의로 놓여지게 되며, 빈 곳이 아닌 곳에 돌을 둘 경우 실격 처리되도록 하였다. 또한 매 턴마다 주어진 15초 이내에 돌을 두지 못할 경우 역시 실격처리된다. 승패를 판단해주고, 가장 최근에 놓여진 돌을 강조해주며, 각 수마다 숫자로 표시해 주는 등 대회 진행 상황을 편리하게 알 수 있도록 구현하였다.
- 대회 관람자는 대국 관전 버튼을 클릭하고, 대국 정보를 입력한 후, 진행중인 게임에 대해 장소에 구애받지 않고 대회 관전이 가능하다.
- 대회 참가자는 위와 같은 플레이어 API를 제공받으며, ‘서버 AI와 대국(1인용)’ 버튼을 클릭하여, 대회 전 언제든지 내장된 AI 알고리즘과 연습 및 테스트가 가능하다. 
 
 

기대 효과 및 장점

알고리즘으로 육목 게임의 승패를 가르는 육목 알고리즘 대회는 2006년 이후 정보 올림피아드 정식 종목으로 채택되었으며, 우리 학교에서도 매년 소프트웨어 페스티벌을 통해 대회를 개최하고 있다.
해당 프로젝트는 기존 대회 플랫폼의 한계에 주목하여 개발이 시작되었다. 먼저 삼성전자의 대회 플랫폼은 제시된 언어와 환경에 맞춰 플레이어의 알고리즘 코드 파일을 대회 서버에 업로드하는 형식이었다. 이는 플레이어들이 원하는 Local 환경과 프로그래밍 언어를 자율적으로 선택하고 활용할 수 없다는 한계가 있었다. 2018년 교내에서 개최되었던 대회에서는 중계를 위해 플레이어들의 알고리즘 결과에 따라 직접 바둑판에 돌을 두어야한다는 번거로움이 있었다.
해당 문제를 해결하고자, 우리는 Restful API를 통해 참가자들의 로컬 컴퓨터와 대회 서버가 통신함으로써 데이터를 전달하도록 하였다. 그리고 POST와 GET을 사용하여 돌을 두고, 게임 정보를 얻는 플레이어의 과정을 규칙에 따라 시각화였다.
따라서, 우리 서비스는 유연성있는 플랫폼 환경을 구축하여 참가자들의 local 환경에서 AI 알고리즘을 돌릴 수 있게 하였으며, 대회를 위한 중계 및 관리 인터페이스를 제공하여 위의 문제점들을 해결하였다. 또한, 기존 플랫폼에는 없는 서버 AI와의 대국 기능은 대회를 준비하는 이들에게 유용하다. 무엇보다, 이 서비스는 11월 개최될 학부 육목 대회에서 사용될 예정으로, smart software application로서의 의의를 가진다.
